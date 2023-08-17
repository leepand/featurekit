import requests
import urllib.parse
import hirlite
import pickle
import os

from datetime import datetime
from datetime import timezone
from datetime import timedelta
from hashlib import sha1


SHA_TZ = timezone(
    timedelta(hours=8),
    name="Asia/Shanghai",
)


def get_week_day():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=11)
    beijing_now = utc_now.astimezone(SHA_TZ)

    return beijing_now.weekday()


def get_bj_day():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=11)
    beijing_now = utc_now.astimezone(SHA_TZ)
    _bj = beijing_now.strftime("%Y-%m-%d")  # 结果显示：'2017-10-07'

    return _bj


def get_yestoday_bj():
    current_date = get_bj_day()  # '2023-07-11'
    date_format = "%Y-%m-%d"
    current_datetime = datetime.strptime(current_date, date_format)
    previous_datetime = current_datetime - timedelta(days=1)
    previous_date = previous_datetime.strftime(date_format)
    return previous_date


def get_bj_day_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=11)
    beijing_now = utc_now.astimezone(SHA_TZ)
    _bj = beijing_now.strftime("%Y-%m-%d %H:%M:%S")  # 结果显示：'2017-10-07'

    return _bj


class FeatureSDK:
    """
    A class representing a Fearure SDK.
    """

    def __init__(self, host="http://1.31.24.138:6901", db_name="", model_name=""):
        """
        初始化FeatureSDK对象。

        参数：
        - host (str)：SDK服务器的基本URL。默认为"http://1.31.24.138:6901"。
        - db_name (str): 数据库的名称。
        - model_name (str): 模型的名称。
        """
        self.host = host
        self.db_store = hirlite.Rlite(f"{db_name}.db", encoding="utf8")
        self.insert_cnt_store_filename = f"{db_name}_insert_cnt.db"
        self.insert_cnt_store = hirlite.Rlite(
            self.insert_cnt_store_filename, encoding="utf8"
        )
        self.db_name = db_name
        self.db_filename = f"{db_name}.db"
        self.model_name = model_name

        self.day = get_bj_day()

    def reset_db(self, dbtype="cnt"):
        """
        重置数据库。

        参数：
        - dbtype (str): 数据库类型。默认为"cnt"。

        如果dbtype为"cnt"，将删除插入计数数据库文件。
        否则，将删除插入计数数据库文件和数据库文件。
        """
        flist = []
        if dbtype == "cnt":
            flist = [self.insert_cnt_store_filename]
        else:
            flist = [self.insert_cnt_store_filename, self.db_filename]

        for filename in flist:

            if os.path.exists(filename):
                os.remove(filename)
                print(f"数据文件'{filename}'已被删除。")
            else:
                print(f"数据文件'{filename}'不存在。")

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

    def push_feature_from_db(self, mode="dev", version=1):
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
        filename = self.db_filename
        remote_name = self.db_filename

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

    def insert_db_local(self, data):
        """
        将数据插入本地数据库。

        参数：
        - data (dict)：要插入的数据。

        返回：
        - result (dict)：插入操作的结果。

        如果data不是字典类型，将返回错误消息。
        否则，将将数据以pickle序列化形式插入数据库，并将插入计数存储到插入计数数据库中。

        返回结果包含操作的状态消息。
        """
        if not isinstance(data, dict):
            return {"status": "error", "msg": "data type must be dict"}
        uid = data["uid"]
        model_key = f"{uid}:{self.model_name}"
        self.db_store.set(model_key, pickle.dumps(data))

        k_cnt = f"{self.day}"
        self.insert_cnt_store.sadd(k_cnt, f"{uid}")
        return {"msg": f"{model_key} is done success"}

    def get_success_cnt(self, date=None):
        """
        获取成功插入计数。

        参数：
        - date (str)：要获取插入计数的日期。默认为None，表示使用当前日期。

        返回：
        - count (int)：成功插入计数。

        如果指定了日期，则获取该日期的插入计数。
        否则，获取今天的插入计数。
        """
        if date is not None:
            k_cnt = f"{date}"
        else:
            k_cnt = f"{self.day}"

        return self.insert_cnt_store.SCARD(k_cnt)
