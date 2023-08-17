import streamlit as st
import hirlite
import pandas as pd


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

data_store = hirlite.Rlite(center_db, encoding="utf8")


st.set_page_config(page_title="Feature Monitor Dashboard", page_icon="📈")


# st.header("YOLO")

select_time = "20s"
day = get_bj_day()
k_cnt = f"{day}"
model_list_sundi = [
    {
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
    }
]

model_list_linshubo = [
    {
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

menu = ["模型元数据", "数据更新"]
choice = st.sidebar.selectbox("Menu", menu)
if choice == "模型元数据":
    "# 📈 Real-Time / Feature Monitor Dashboard"
    st.subheader(f"@孙迪 执掌的模型信息：")
    for m in model_list_sundi:
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

    # 假设你有一个名为data的字典，其中包含要转换为DataFrame的数据
    data = {
        "模型名称": ["付费弹窗离线模型", "付费弹窗离线模型", "流失模型-首局体验策略"],
        "model_name": ["probs", "probs", "probs"],
        "db_name": [
            "offline_popup_model",
            "offline_popup_model",
            "offline_popup_model",
        ],
        "成功条数": [25, 30, 35],
        "实际条数": [24, 31, 35],
        "更新差值": [-1, 1, 0],
        "更新日期": ["2023-8-16", "2023-8-17", "2023-8-18"],
        "责任人": ["孙迪", "孙迪", "林书博"],
    }

    def color_survived(val):
        color = "red" if val > 0 else "yellow" if val < 0 else "green"
        return f"background-color: {color}"

    df = pd.DataFrame(data)
    st.markdown("### Detailed Data Update View")
    st.table(
        df[["模型名称", "model_name", "db_name", "成功条数", "实际条数", "更新差值", "更新日期", "责任人"]]
        .sort_values(["更新差值"], ascending=False)
        .reset_index(drop=True)
        .head(20)
        .style.applymap(color_survived, subset=["更新差值"])
    )

    # 使用Pandas将字典转换为DataFrame

    # st.dataframe(df)
