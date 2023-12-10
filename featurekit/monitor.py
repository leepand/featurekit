import streamlit as st
import hirlite
import pandas as pd
import os
import pickle

from datetime import datetime
from datetime import timezone
from datetime import timedelta
from hashlib import sha1


SHA_TZ = timezone(
    timedelta(hours=8),
    name="Asia/Shanghai",
)


def get_file_size(file_path):
    # 获取文件大小（以字节为单位）
    file_size = os.path.getsize(file_path)
    print("文件大小（字节）:", file_size)

    # 获取文件大小（以可读格式显示）
    file_size_readable = os.path.getsize(file_path)
    size_suffixes = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    while file_size_readable >= 1024 and index < len(size_suffixes) - 1:
        file_size_readable /= 1024
        index += 1
    file_size_readable = f"{file_size_readable:.2f} {size_suffixes[index]}"
    return file_size_readable


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

data_store = hirlite.Rlite(center_db, encoding="utf8")


st.set_page_config(page_title="Feature Monitor Dashboard", page_icon="📈")


# st.header("YOLO")

select_time = "20s"
day = get_bj_day()
k_cnt = f"{day}"
model_list_sundi = [
    {
        "owner": "sundi",
        "model_name": "probs",
        "model_name_desc": "付费弹窗离线模型",
        "db_name": "offline_popup_model",
        "data_exm": {
            "B级活动": 0.4004315146443851,
            "DashMax": 0.07602124031689082,
            "MissionBadge": 0.48872136827031,
            "促销": 0.01274745428560601,
            "宝石": 0.01651469980769244,
            "押分猫": 0.0055074131807449815,
            "锤子": 5.630949437083146e-05,
            "uid": "10739979",
            "created_at": "2023-08-16",
        },
    },
    {
        "owner": "sundi",
        "model_name": "navig_promotion",
        "model_name_desc": "航海定价促销付费/道具先验",
        "db_name": "navig_pricing_promotion_model",
        "data_exm": {
            "uid": "7765633",
            "data": {
                "booster": {
                    "golden_spin": 0.4545,
                    "rapid_set": 0.0909,
                    "card_blast": 0.1818,
                    "build_fever": 0.2727,
                }
            },
            "model_type": "navig_promotion",
            "current_date": "2023-08-17",
        },
    },
    {
        "owner": "sundi",
        "model_name": "uni_pricing",
        "db_name": "uni_pricing_prior",
        "model_name_desc": "uni定价近1个月的DC项付费先验",
        "data_exm": {
            "uid": "27513228",
            "model_type": "uni_pricing",
            "pay": {"DC2": 1, "DC9": 1},
            "current_date": "2023-06-29",
        },
    },
    {
        "owner": "sundi",
        "model_name": "uni_pricing_spty",
        "model_name_desc": "uni定价近1个月的sp_ty购买偏好",
        "db_name": "uni_pricing_prior_spty",
        "data_exm": {
            "uid": "27513228",
            "model_type": "uni_pricing_spty",
            "pay": {
                "last_7days": {"B13": 11.99, "A01": 1.99, "E05": 1.99},
                "last_month": {"B13": 11.99, "A01": 1.99, "E05": 1.99},
            },
            "current_date": "2023-07-10",
        },
    },
    {
        "owner": "sundi",
        "model_name": "peek_experience",
        "model_name_desc": "巅峰体验潜在用户群",
        "db_name": "peek_experience_v1",
        "data_exm": {
            "uid": "27513228",
            "model_type": "peek_experience",
            "peek_state": 0.08002756829971648,
            "current_date": "2023-08-17",
        },
    },
]

model_list_linshubo = [
    {
        "owner": "linshubo",
        "model_name": "churn_spinux_model",
        "model_name_desc": "流失模型-首局体验策略",
        "db_name": "offline_churn_spinux_model",
        "data_exm": {
            "uid": "14542135",
            "model_type": "offline_churn_spinux_model",
            "churn_probs": 0.7997267011191374,
            "created_at": "2023-06-26 09:11:16.067430",
            "shap_singal": {"features": ["days_30"], "if_recom": 1},
        },
    }
]

# selected_genre = data_store.SCARD(k_cnt)
# st.subheader(f"模型：peek_experience_v1,成功条数: {selected_genre}, 执行时间: {select_time}")
today = get_bj_day()
current_date = datetime.strptime(today, "%Y-%m-%d")  # 将字符串转换为datetime对象
date_list = []

# 通过循环生成前7天的日期列表
for i in range(7):
    delta = timedelta(days=i)  # 创建一个时间间隔对象，表示i天
    date = current_date - delta  # 当前日期减去时间间隔，获得前i天的日期
    date_list.append(date.strftime("%Y-%m-%d"))  # 将日期对象转换为字符串并添加到列表中


menu = ["模型元数据", "数据更新"]
choice = st.sidebar.selectbox("Menu", menu)
if choice == "模型元数据":
    "# 📈 Real-Time / Feature Monitor Dashboard"
    st.subheader(f"@孙迪 执掌的模型信息：")
    for index, m in enumerate(model_list_sundi):
        model_name = m["model_name"]
        model_name_desc = m["model_name_desc"]
        data_exm = m["data_exm"]
        db_name = m["db_name"]
        st.markdown(f"#### {index+1}、{model_name_desc}")
        st.text(f"model_name：{model_name}\n")
        st.text(f"model_name_desc:{model_name_desc}\n")
        st.text(f"db_name:{db_name}\n")
        st.text(f"数据示例:\n")
        st.json(data_exm)
        st.text(f"\n")
        st.text(f"数据更新信息: 暂无\n")

    st.subheader(f"@林书博 执掌的模型信息：")

    for m in model_list_linshubo:
        model_name = m["model_name"]
        model_name_desc = m["model_name_desc"]
        data_exm = m["data_exm"]
        db_name = m["db_name"]
        st.markdown(f"#### 1、{model_name_desc}")
        st.text(f"model_name：{model_name}\n")
        st.text(f"model_name_desc:{model_name_desc}\n")
        st.text(f"db_name:{db_name}\n")
        st.text(f"数据示例:\n")
        st.json(data_exm)
        st.text(f"\n")
        st.text(f"数据更新信息: 暂无\n")
elif choice == "数据更新":
    "# 📈 Real-Time / Feature Monitor Dashboard"

    # 假设你有一个名为data的字典，其中包含要转换为DataFrame的数
    time_menu = ["今天", "昨天"]
    time_menu = date_list
    options = st.sidebar.selectbox("时间区间", time_menu)

    model_name_desc_list = []
    model_name_list = []
    success_cnt_list = []
    real_cnt_list = []
    update_gap_list = []
    update_date_list = []
    owner_list = []
    size_of_data_list = []

    if options == "今天":
        _date = get_bj_day()
    else:
        _date = options  # get_yestoday_bj()

    merged_list = model_list_sundi + model_list_linshubo
    for model_info in merged_list:
        model_name = model_info["model_name"]
        model_desc = model_info["model_name_desc"]
        db_name = model_info["db_name"]
        owner = model_info["owner"]
        query_date = _date
        data_store_key = f"{model_name}:{query_date}"
        db_info = data_store.get(data_store_key)

        model_name_desc_list.append(model_desc)
        model_name_list.append(model_name)

        if owner == "sundi":
            _owner = "孙迪"
        elif owner == "linshubo":
            _owner = "林书博"
        else:
            _owner = "暂无"
        if db_info is None:
            succ_cnt = "暂无数据"
            real_cnt = "暂无数据"
            update_gap = -1
            data_size = "暂无数据"
            _current_date = _date
        else:
            _data = pickle.loads(db_info)
            succ_cnt = _data["success_insert_cnt"]
            real_cnt = _data["correct_data_cnt"]
            _current_date = _data["current_date"]
            update_gap = real_cnt - succ_cnt
            p = _data["data_path"]
            file = f"{p}/{db_name}.db"
            try:
                data_size = get_file_size(file)
            except:
                data_size = f"file {file} not found"

        size_of_data_list.append(data_size)
        update_gap_list.append(update_gap)
        real_cnt_list.append(real_cnt)
        success_cnt_list.append(succ_cnt)
        update_date_list.append(_current_date)
        owner_list.append(_owner)

    data = {
        "模型名称": model_name_desc_list,
        "model_name": model_name_list,
        "成功条数": success_cnt_list,
        "实际条数": real_cnt_list,
        "更新差值": update_gap_list,
        "数据大小": size_of_data_list,
        "更新日期": update_date_list,
        "责任人": owner_list,
    }

    def color_survived(val):
        color = "red" if val > 0 else "yellow" if val < 0 else "green"
        return f"background-color: {color}"

    df = pd.DataFrame(data)
    st.markdown("### Detailed Data Update View")
    st.table(
        df[["模型名称", "model_name", "成功条数", "实际条数", "更新差值", "数据大小", "更新日期", "责任人"]]
        .sort_values(["更新差值"], ascending=False)
        .reset_index(drop=True)
        .head(20)
        .style.applymap(color_survived, subset=["更新差值"])
    )

    # st.text(f"{date_list}")

    # 使用Pandas将字典转换为DataFrame

    # st.dataframe(df)
