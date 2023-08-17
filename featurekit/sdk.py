import requests
import urllib.parse


class FeatureSDK:
    """
    A class representing a Fearure SDK.
    """

    def __init__(self, host="http://1.31.24.138:6901"):
        """
        Initializes the FearureSDK object.

        Parameters:
        - host (str): The base URL of the SDK server. Defaults to "http://1.31.24.138:6901".
        """
        self.host = host

    def _request(self, method, endpoint, **kwargs):
        """
        Sends an HTTP request to the specified endpoint.

        Parameters:
        - method (str): The HTTP method for the request (e.g., "GET", "POST", "PUT", "DELETE").
        - endpoint (str): The endpoint URL for the request.
        - kwargs: Additional keyword arguments to be passed to the requests library.

        Returns:
        - r (requests.Response): The response object obtained from the HTTP request.

        Raises:
        - ValueError: If the HTTP response contains an error (status code >= 400).
        - requests.exceptions.HTTPError: If an HTTP exception occurs during the request.
        - requests.exceptions.JSONDecodeError: If there is an error decoding the response JSON.
        """
        # Construct the full URL by joining the base host and the endpoint
        url = urllib.parse.urljoin(self.host, endpoint)
        print(url)

        # Send the HTTP request
        r = requests.request(method=method, url=url, **kwargs)

        try:
            r.raise_for_status()  # Raise an exception if the response status code is >= 400
        except requests.exceptions.HTTPError as e:
            try:
                raise ValueError(
                    r.json()
                ) from e  # Try to parse the response JSON and raise a ValueError
            except requests.exceptions.JSONDecodeError:
                raise e

        return r

    def push_feature(self, filename, remote_name, mode, version=1):
        """
        Pushes a feature file to the SDK server.

        Parameters:
        - filename (str): The path to the local feature file.
        - remote_name (str): The name to be assigned to the feature file on the server.
        - mode (str): The mode of the feature file.
        - version (int): The version of the feature file. Defaults to 1.

        Returns:
        - r (dict): The JSON response obtained from the server.

        Raises:
        - ValueError: If the HTTP response contains an error (status code >= 400).
        - requests.exceptions.HTTPError: If an HTTP exception occurs during the request.
        - requests.exceptions.JSONDecodeError: If there is an error decoding the response JSON.
        """
        with open(filename, "rb") as f:
            _f = {"file": f}
            r = self._request(
                "POST",
                "models/push",
                data={
                    "mode": mode,
                    "version": version,
                    "remote_name": remote_name,
                },
                files=_f,
            ).json()
        return r