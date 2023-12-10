from featurekit import FeatureSDK
import pandas as pd
import time
import datetime
import pytz
import schedule
import json
import traceback

from google.cloud import bigquery
from rocketry import Rocketry
from datetime import timezone, timedelta, datetime
from rocketry.conds import (
    time_of_day,
    every,
    hourly,
    daily,
    weekly,
    after_success,
    true,
    false,
)
import sys
import os

center_config_path = "/home/leepand/sundi/center_config/"
center_log_path = "/home/leepand/sundi/center_logs/schedule_log/"
center_error_log_path = "/home/leepand/sundi/center_logs/error_log/"

sys.path.append(center_config_path)

from BigQueryReader import *
from BigQueryUploader import upload_to_bq

app = Rocketry()

MODE = "dev"


@app.task("daily after 02:20")
def main():
    # 读取文件
    day_create = str(((datetime.now() + timedelta(hours=-3)).date()))

    log_file = os.path.join(center_log_path, "dong_peek_experience_schedule.txt")
    log_error_file = os.path.join(
        center_error_log_path, f"dong_peek_experience_error_{day_create}.txt"
    )

    feature_peak = FeatureSDK(
        db_name="peek_experience_v1", model_name="peek_experience", db_path="./db"
    )

    with open(log_file, "a") as f:
        f.write(f"开始读取文件：{str(datetime.now() + timedelta(hours = 8))}\n")

    bq_reader = BigQueryReader()
    query = f"""
              SELECT * FROM `seateam.stats.peek_experience_uid_list`
            """
    data = bq_reader.get_dataset(query)
    data = pd.DataFrame(data.to_dict())
    num_rows = data.shape[0]
    data.current_date = data.current_date.astype("string")

    with open(log_file, "a") as f:
        f.write(
            f"读取文件结束：{str(datetime.now() + timedelta(hours = 8))}\n读取文件大小：{data.shape}\n"
        )

    a = 0
    b = 0
    for i in data.index:
        try:
            row = data.loc[i]
            single_dict = {}
            single_dict["uid"] = row.uid
            single_dict["model_type"] = "peek_experience"
            single_dict["peek_state"] = row.peek_state
            single_dict["current_date"] = row.current_date
            # r = requests.post('http://1.31.24.138:6000/predict/recomserver',
            #                          json = single_dict)
            # user_key = f"{row.uid}:peek_experience"
            # db_store.set(user_key,pickle.dumps(single_dict))
            # test.push_feature("test_peak.db",remote_name="test_peak.db",mode="dev")

            feature_peak.insert_db_local(single_dict)
            a += 1
            if a % 30000 == 0:
                with open(log_file, "a") as f:
                    f.write(
                        f"    已经写入{a}行 {str(datetime.now() + timedelta(hours = 8))}\n"
                    )

        except:
            # 230816 with open(f"./remote_errors/{row.uid}_error.txt", "w") as g:
            # 230816    g.write(str(traceback.format_exc()))
            b += 1
            with open(log_error_file, "a") as f:
                f.write(
                    f"{day_create} : 「第{a}条数据报错，目前已有{b}条未写入」\n {str(traceback.format_exc())}\n"
                )

    with open(log_file, "a") as f:
        f.write(f"写入结果完毕：{str(datetime.now() + timedelta(hours = 8))}\n")

    # cnt = feature_peak.get_success_cnt()
    feature_peak.push_feature_from_db(num_rows, mode=MODE, version=1)


if __name__ == "__main__":
    app.run()
