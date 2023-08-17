import streamlit as st
import hirlite

from datetime import datetime
from datetime import timezone
from datetime import timedelta
from hashlib import sha1


SHA_TZ = timezone(
    timedelta(hours=8),
    name="Asia/Shanghai",
)


def number_format(number):
    return "{:,}".format(number)


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


center_db = "/home/leepand/center_db/monitor.db"

insert_cnt_store = hirlite.Rlite(model_file, encoding="utf8")


st.set_page_config(page_title="Feature Monitor Dashboard", page_icon="📈")


# st.header("YOLO")
"# 📈 Real-Time / Feature Monitor Dashboard"
select_time = "20s"
day = get_bj_day()
k_cnt = f"{day}"

selected_genre = insert_cnt_store.SCARD(k_cnt)
st.subheader(f"模型：peek_experience_v1,成功条数: {selected_genre}, 执行时间: {select_time}")
