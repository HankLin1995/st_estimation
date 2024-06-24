# import streamlit as st
import json
from datetime import date, datetime
import requests

# 模拟一些 session state 数据
# st.session_state.current_page = "render_page0"
# st.session_state.submitted = False
# st.session_state.costs = {
#     "open_channel": {"name": "渠道工程", "unit_cost": 0, "length": 0, "total_cost": 0},
#     "bridge": {"name": "版橋工程", "unit_cost": 0, "quantity": 0, "total_cost": 0},
#     "wall": {"name": "擋土牆", "unit_cost": 0, "length": 0, "total_cost": 0},
#     "road": {"name": "道路工程", "unit_cost": 0, "quantity": 0, "total_cost": 0},
#     "falsework": {"name": "版樁工程", "unit_cost": 0, "quantity": 0, "total_cost": 0},
# }
# st.session_state.totalcost = 0
# st.session_state.inf = {
#     "work_place": "",
#     "work_place2": "",
#     "work_station": "",
#     "work_name": "",
#     "work_benefit": "",
#     "work_place_detail": "",
#     "work_water_check": False,
#     "work_start_date": date.today(),
#     "work_end_date": date.today(),
# }

# 自定义 JSON 序列化器，用于处理日期字段
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

# 定义一个函数，将 st.session_state 转换为 JSON
# def session_state_to_json():
#     selected_fields = ["costs", "inf"] # 指定需要转换的字段
#     session_state_dict = {key: value for key, value in st.session_state.items()if key in selected_fields}
#     json_data = json.dumps(session_state_dict, cls=DateTimeEncoder)
#     return json_data

def st_to_json(st_dict):
    selected_fields = ["inf","coords"] # 指定需要转换的字段
    st_dict = {key: value for key, value in st_dict.items()if key in selected_fields}
    # st_dict = {key: value for key, value in st_dict.items()}
    json_data = json.dumps(st_dict, cls=DateTimeEncoder)
    return json_data

# # 使用函数并展示结果

# st.session_state['inf']['work_start_date']=st.date_input("開始日期")#, st.session_state.inf.work_start_date)
# st.session_state['inf']['work_end_date']=st.date_input("結束日期")#, st.session_state.inf.work_end_date)

# json_result = session_state_to_json()
# st.write(st.session_state)
# st.write(json_result)

# if st.button("Submit"):

#     # 設置 Google Apps Script Web 應用程式的 URL
#     url = "https://script.google.com/macros/s/AKfycbz6CWS_HnAATXAMwJBJhIELbAoWsgcYJFkNxpgldA96m1SkWVeEgy4l1EyXeyW60gmK/exec"

#     with st.spinner("Sending request..."):

#         # 發送 POST 請求並傳遞 JSON 資料
#         response = requests.post(url, data=json_result)

#         # 檢查請求是否成功
#         if response.status_code == 200:
#             st.write("Request successful!")
#         else:
#             st.write("Error:", response.status_code)
