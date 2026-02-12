import streamlit as st
import pandas as pd
from tabs import render_falsework_tab, render_channel_tab, render_bridge_tab, render_road_tab, render_wall_tab
import openpyxl
from openpyxl.drawing.image import Image
import os,io
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import datetime
import requests
import json
from myImage import insert_image
from openpyxl.drawing.image import Image as OpenpyxlImage
from json_test import st_to_json
from datetime import datetime,date

# 自定义 JSON 序列化器，用于处理日期字段

def get_basic_price_data():
    unit_price_data = {
        '材料': ['140kg/cm2混凝土','175kg/cm2混凝土' ,'210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板','AC','碎石級配','CLSM'],
        '單價': [2700, 2750, 2900, 31, 660, 550,360,790,1460],  
        '單位': ['m3','m3', 'm3', 'kg', 'm2','m2','m2','m3','m3']
    }
    return pd.DataFrame(unit_price_data)

def get_falsework_price_data():
    unit_price_data = {
        '材料': ['鋼板樁L=4.5M', '鋼板樁L=6M','鋼板樁L=7M','鋼板樁L=9M','鋼板樁L=13M','鋼軌樁L=4M', '鋼軌樁L=6M','鋼軌樁L=7M','鋼軌樁L=10M','鋼軌樁L=12M'],
        '單價': [2310,2910,3420,3750,4410,1620,1800,1950,2850,3400],  
        '單位': ['每進行m']*10
    }
    return pd.DataFrame(unit_price_data)

def get_cost_data(coe_other):

    my_other_cost=0

    cost_data = []
    for key, item in st.session_state['costs'].items():

        my_other_cost=my_other_cost+int(item['total_cost'])
        
        cost_data.append({
            '項目': item['name'],
            '總價': item['total_cost'],
            '單位': '元'
        })

    cost_data.append({
        '項目': '雜項及其他',
        '總價': int(my_other_cost*coe_other),
        '單位': '元' 
    })

    return pd.DataFrame(cost_data)

def generate_cost_report(costs,other_coefficient, indirect_coefficient):
    report = []
    total_direct_cost = 0
    index = 1

    for key, item in costs.items():
        total_cost = item['total_cost']
        if total_cost == 0:
            continue
        
        if key in ['road', 'falsework']:
            description = f"{total_cost:,.0f}元"
        else:
            if 'length' in item:
                description = f"{item['unit_cost']:,.0f}元/每進行m * {item['length']:,.0f}m"
            elif 'quantity' in item:
                description = f"{item['unit_cost']:,.0f}元/每座 * {item['quantity']:,.0f}座"
            description += f" = {total_cost:,.0f}元"
        
        report.append(f"{index}. {item['name']}: {description}")
        total_direct_cost += total_cost
        index += 1

    other_cost=total_direct_cost*other_coefficient
    description = f"{other_cost:,.0f}元"
    report.append(f"{index}. 雜項及其他: {description}")

    total_direct_cost=total_direct_cost+other_cost

    indirect_cost = round(total_direct_cost * (1+indirect_coefficient),-3)-total_direct_cost
    total_cost = total_direct_cost + indirect_cost

    report.append(f"\n直接工程費 = {total_direct_cost:,.0f}元")
    report.append(f"間接工程費 = 直接工程費 * {indirect_coefficient} = {indirect_cost:,.0f}元")
    report.append(f"\n總工程費 = {total_cost:,.0f}元")

    st.session_state.totalcost=total_cost
    st.session_state['inf']['job_cost'] = total_cost

    return "\n".join(report)

def check_for_blank_values(data):

    blank_fields = []
    for key, value in data.items():
        # print(type(value), value)
        if type(value) == str and value=="":
            blank_fields.append(getTitle(key))
        elif type(value) == bool or type(value) == int:
            continue  # 不检查布尔值或整数
        elif type(value) == datetime and not value:
            blank_fields.append(getTitle(key))
        elif type(value) == date and not value:
            blank_fields.append(getTitle(key))
        elif type(value) == float and value == 0:
            blank_fields.append(getTitle(key))
        elif value is None:
            blank_fields.append(getTitle(key))
        else:
            continue#st.warning(f"未处理的数据类型: {type(value)} for key: {key}")

    return blank_fields

def getTitle(engname):

    myDict={
        'work_place':'縣市',
        'work_place2':'鄉鎮市',
        'work_name':'工程名稱',
        'work_benefit':'受益面積',
        'work_start_date':'最佳施工起始日期',
        'work_end_date':'最佳施工結束日期',
        'work_manage':'分處',
        'work_station':'工作站',
        'job_cost':'概估經費',
        'job_length':'水路長度'
    }

    return myDict[engname]

def generateXLS(report):

    # Check input empty
    blank_fields = check_for_blank_values(st.session_state['inf'])

    if len(st.session_state['coords'])!=3:
        st.warning("請確認座標是否有三個點!")
        exit()

    if st.session_state['inf']['work_start_date'] == date(2024,1,1):
        st.warning("請確認最佳施工起始日期!")
        exit()

    if st.session_state['inf']['work_end_date'] == date(2024,1,1):
        st.warning("請確認最佳施工結束日期!")
        exit()      

# 显示空白值
    if blank_fields:
        # st.warning(f"請將空白內容填上:")
        for r in range(len(blank_fields)):
            st.warning(f"\n\n{blank_fields[r]} :空白!")
        exit()
   
        # st.warning(f"請將空白內容填上:\n\n{', '.join(blank_fields)}")
    else:

        st.session_state['inf']['timestamp'] = datetime.now()

        if 'coords' in st.session_state and len(st.session_state['coords']) >= 2:
            # Extract the coordinates
            X1 = st.session_state['coords'][0]['twd97_x']
            Y1 = st.session_state['coords'][0]['twd97_y']
            X2 = st.session_state['coords'][1]['twd97_x']
            Y2 = st.session_state['coords'][1]['twd97_y']
            # X3 = st.session_state['coords'][2]['twd97_x']
            # Y3 = st.session_state['coords'][2]['twd97_y']       
        else:
            # 處理 `st.session_state['coords']` 尚未初始化或長度不是2 的情況
            # 可以在這裡設定適當的預設值或者發出警告訊息
            X1, Y1, X2, Y2 = 0, 0, 0, 0  # 設定預設值為0，你也可以根據需求設定其他值
            # st.warning("請手動輸入兩個座標至概要表")

        workbook = openpyxl.load_workbook('./template/PLAN.xlsx')
        sheet = workbook["概要表"]

        sheet.cell(row=3, column=8).value = report
        sheet.cell(row=16,column=4).value=X1
        sheet.cell(row=17,column=4).value=Y1
        sheet.cell(row=18,column=4).value=X2
        sheet.cell(row=19,column=4).value=Y2
        sheet.cell(row=2,column=1).value=st.session_state['inf']['work_place'] +st.session_state['inf']['work_place2']
        sheet.cell(row=3,column=2).value=st.session_state['inf']['work_station']
        sheet.cell(row=6,column=2).value=st.session_state['inf']['work_name']
        sheet.cell(row=9,column=2).value=st.session_state.totalcost
        sheet.cell(row=14,column=2).value="受益面積"+st.session_state['inf']['work_benefit']+"ha"

        if st.session_state['inf']['work_place_detail']=="已取得並確認妥處":
            sheet.cell(row=20,column=2).value=' (V)'
        else:
            sheet.cell(row=21,column=2).value=' (V)'

        if st.session_state['inf']['work_water_check']=="是":
            sheet.cell(row=22,column=1).value='是否需配合斷水期施工：     （V）是    （  ）否'
        else:
            sheet.cell(row=22,column=1).value='是否需配合斷水期施工：     （  ）是    （V）否'

        work_start_date = st.session_state['inf']['work_start_date']
        work_end_date = st.session_state['inf']['work_end_date']

        start_date_str = work_start_date.strftime("%Y年%m月") if work_start_date else "未指定"
        end_date_str = work_end_date.strftime("%Y年%m月") if work_end_date else "未指定"

        sheet.cell(row=22,column=7).value= f"最佳施工期：{start_date_str} ~ {end_date_str}"

        if st.session_state.uploaded_file1 is not None:
            img1_file = io.BytesIO(st.session_state.uploaded_file1.getvalue())
            img1 = OpenpyxlImage(img1_file)
            insert_image(sheet,img1,3,5)
        if st.session_state.uploaded_file2 is not None:
            img2_file = io.BytesIO(st.session_state.uploaded_file2.getvalue())
            img2 = OpenpyxlImage(img2_file)
            insert_image(sheet,img2,14,5)
        if st.session_state.uploaded_file3 is not None:
            img3_file = io.BytesIO(st.session_state.uploaded_file3.getvalue())
            img3 = OpenpyxlImage(img3_file)
            insert_image(sheet,img3,14,8)
        if st.session_state.uploaded_file4 is not None:
            img4_file = io.BytesIO(st.session_state.uploaded_file4.getvalue())
            img4 = OpenpyxlImage(img4_file)
            insert_image(workbook["位置圖"],img4,3,1)

        sheet = workbook["提報明細表"]

        sheet.cell(row=6,column=1).value=1
        sheet.cell(row=6,column=2).value=st.session_state['inf']['work_name']
        sheet.cell(row=6,column=3).value=st.session_state['costs']['open_channel']['length']
        sheet.cell(row=6,column=5).value=st.session_state['inf']['work_benefit']
        sheet.cell(row=6,column=6).value=st.session_state['inf']['work_place']
        sheet.cell(row=6,column=7).value=st.session_state['inf']['work_place2']
        if st.session_state['inf']['work_place_detail']=="已取得並確認妥處":
            sheet.cell(row=6,column=8).value='V'
        sheet.cell(row=6,column=9).value=st.session_state.totalcost/1000

        # 新增幾何參數分頁
        if "幾何參數" not in workbook.sheetnames:
            geometry_sheet = workbook.create_sheet("幾何參數")
        else:
            geometry_sheet = workbook["幾何參數"]

        # 設定標題
        geometry_sheet.cell(row=1, column=1).value = "工程幾何參數表"
        geometry_sheet.cell(row=2, column=1).value = "項目"
        geometry_sheet.cell(row=2, column=2).value = "參數名稱"
        geometry_sheet.cell(row=2, column=3).value = "數值"
        geometry_sheet.cell(row=2, column=4).value = "單位"

        row_num = 3

        # 渠道工程參數
        if 'channel_width' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "渠道工程"
            geometry_sheet.cell(row=row_num, column=2).value = "寬度b"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('channel_width', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        if 'channel_height' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "渠道工程"
            geometry_sheet.cell(row=row_num, column=2).value = "高度H"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('channel_height', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        if 'channel_length' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "渠道工程"
            geometry_sheet.cell(row=row_num, column=2).value = "長度L"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('channel_length', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        # 版橋工程參數
        if 'bridge_width' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "版橋工程"
            geometry_sheet.cell(row=row_num, column=2).value = "寬度W"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('bridge_width', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        if 'bridge_length' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "版橋工程"
            geometry_sheet.cell(row=row_num, column=2).value = "每座長度L"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('bridge_length', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        if 'bridge_cnt' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "版橋工程"
            geometry_sheet.cell(row=row_num, column=2).value = "數量"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('bridge_cnt', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "座"
            row_num += 1

        # 擋土牆參數
        if 'op' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "擋土牆"
            geometry_sheet.cell(row=row_num, column=2).value = "型式"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('op', '')
            geometry_sheet.cell(row=row_num, column=4).value = ""
            row_num += 1

        if 'wall_height_cm' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "擋土牆"
            geometry_sheet.cell(row=row_num, column=2).value = "高度(重力式)"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('wall_height_cm', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "cm"
            row_num += 1

        if 'wall2_height_cm' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "擋土牆"
            geometry_sheet.cell(row=row_num, column=2).value = "高度(懸臂式)"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('wall2_height_cm', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "cm"
            row_num += 1

        if 'wall_cnt' in st.session_state:
            geometry_sheet.cell(row=row_num, column=1).value = "擋土牆"
            geometry_sheet.cell(row=row_num, column=2).value = "施作長度"
            geometry_sheet.cell(row=row_num, column=3).value = st.session_state.get('wall_cnt', 0)
            geometry_sheet.cell(row=row_num, column=4).value = "m"
            row_num += 1

        # 道路工程參數
        if 'data2' in st.session_state and st.session_state['data2']:
            for i, road_data in enumerate(st.session_state['data2']):
                if len(road_data) >= 4:
                    geometry_sheet.cell(row=row_num, column=1).value = "道路工程"
                    geometry_sheet.cell(row=row_num, column=2).value = f"材料類型{i+1}"
                    geometry_sheet.cell(row=row_num, column=3).value = road_data[0]
                    geometry_sheet.cell(row=row_num, column=4).value = ""
                    row_num += 1
                    
                    geometry_sheet.cell(row=row_num, column=1).value = "道路工程"
                    geometry_sheet.cell(row=row_num, column=2).value = f"施作面積{i+1}"
                    geometry_sheet.cell(row=row_num, column=3).value = road_data[2]
                    geometry_sheet.cell(row=row_num, column=4).value = "m2"
                    row_num += 1

        # 版樁工程參數
        if 'data' in st.session_state and st.session_state['data']:
            for i, pile_data in enumerate(st.session_state['data']):
                if len(pile_data) >= 5:
                    geometry_sheet.cell(row=row_num, column=1).value = "版樁工程"
                    geometry_sheet.cell(row=row_num, column=2).value = f"材料類別{i+1}"
                    geometry_sheet.cell(row=row_num, column=3).value = pile_data[0]
                    geometry_sheet.cell(row=row_num, column=4).value = ""
                    row_num += 1
                    
                    geometry_sheet.cell(row=row_num, column=1).value = "版樁工程"
                    geometry_sheet.cell(row=row_num, column=2).value = f"材料長度{i+1}"
                    geometry_sheet.cell(row=row_num, column=3).value = pile_data[1]
                    geometry_sheet.cell(row=row_num, column=4).value = "m"
                    row_num += 1
                    
                    geometry_sheet.cell(row=row_num, column=1).value = "版樁工程"
                    geometry_sheet.cell(row=row_num, column=2).value = f"施作長度{i+1}"
                    geometry_sheet.cell(row=row_num, column=3).value = pile_data[3]
                    geometry_sheet.cell(row=row_num, column=4).value = "m"
                    row_num += 1

        # 渠道工程材料計算表
        if 'channel_material_table' in st.session_state and st.session_state['channel_material_table']:
            row_num += 2
            geometry_sheet.cell(row=row_num, column=1).value = "渠道工程材料計算表(每進行米)"
            row_num += 1
            
            geometry_sheet.cell(row=row_num, column=1).value = "材料"
            geometry_sheet.cell(row=row_num, column=2).value = "數量"
            geometry_sheet.cell(row=row_num, column=3).value = "單位"
            geometry_sheet.cell(row=row_num, column=4).value = "單價"
            geometry_sheet.cell(row=row_num, column=5).value = "複價"
            row_num += 1
            
            for material in st.session_state['channel_material_table']:
                geometry_sheet.cell(row=row_num, column=1).value = material.get('材料', '')
                geometry_sheet.cell(row=row_num, column=2).value = material.get('數量', 0)
                geometry_sheet.cell(row=row_num, column=3).value = material.get('單位', '')
                geometry_sheet.cell(row=row_num, column=4).value = material.get('單價', 0)
                geometry_sheet.cell(row=row_num, column=5).value = material.get('複價', 0)
                row_num += 1

        output_file = 'example.xlsx'

        workbook.save(output_file)
        with open(output_file, 'rb') as f:
            bytes_data = f.read()
        btn=st.sidebar.download_button(label='計算成果下載', data=bytes_data, file_name=output_file, type='primary')
        os.remove(output_file)
        # savedata()

def savedata():
    json_result = st_to_json(st.session_state)
    # 設置 Google Apps Script Web 應用程式的 URL
    url =st.secrets.GAS_URL 
    with st.sidebar:
        with st.spinner("...資料儲存中..."):
            # 發送 POST 請求並傳遞 JSON 資料
            response = requests.post(url, data=json_result)
            # 檢查請求是否成功
            if response.status_code == 200:
                st.write("資料儲存成功!")
            else:
                st.write("Error:", response.status_code)

def render_page0():

    # st.subheader(":dart:歡迎來到主頁面")

    col1,col2,col3=st.columns([5,1,5])

    with col1:

        with open("./md/SP.md", "r", encoding="utf-8") as file:
            markdown_text = file.read()

        st.markdown(markdown_text)


    with col3:

        with open("./md/log.md", "r", encoding="utf-8") as file:
            markdown_text = file.read()

        st.markdown(markdown_text,True) 

    st.session_state.current_page = 'render_page0'

def render_page1():

        # 检查并确保日期类型或为空
    work_start_date = st.session_state['inf']['work_start_date']
    work_end_date = st.session_state['inf']['work_end_date']

    if isinstance(work_start_date, (str,)):
        work_start_date = None

    if isinstance(work_end_date, (str,)):
        work_end_date = None

    st.subheader("工程基本資料填報")

    col1,col2=st.columns([1,1])

    with col1:

        col1_left,col1_right=st.columns([1,1])

        with col1_left:
            st.session_state['inf']['work_place'] = st.text_input("縣市別", value=st.session_state['inf']['work_place'])
            # st.session_state['inf']['work_place2'] = st.text_input("鄉鎮市別", value=st.session_state['inf']['work_place2'])
            st.session_state['inf']['work_manage'] = st.selectbox("分處", options=["斗六分處","西螺分處","虎尾分處","北港分處","林內分處"])
        with col1_right:
            st.session_state['inf']['work_place2'] = st.text_input("鄉鎮市別", value=st.session_state['inf']['work_place2'])
            # st.session_state['inf']['work_manage'] = st.selectbox("分處", options=["斗六分處","西螺分處","虎尾分處","北港分處","林內分處"])
            st.session_state['inf']['work_station'] = st.text_input("工作站", value=st.session_state['inf']['work_station'])
        st.session_state['inf']['work_name'] = st.text_input("水路名稱", value=st.session_state['inf']['work_name'])
        st.session_state['inf']['work_benefit'] = st.text_input("受益面積(ha)", value=st.session_state['inf']['work_benefit'])
        
        st.markdown("---")
        st.session_state['inf']['work_place_water'] = st.selectbox("水路用地", options=["處有地","私有地","公有地"])
        st.session_state['inf']['work_place_detail'] = st.selectbox("工程用地", options=["已取得並確認妥處","尚未取得或尚未妥處"])
        # st.session_state['inf']['work_place_detail'] = st.radio("工程用地", options=["已取得並確認妥處","尚未取得或尚未妥處"], 
                                                            # index=0 if st.session_state['inf']['work_place_detail'] != "" else 1)
        # st.session_state['inf']['work_water_check'] = st.selectbox("是否需要配合斷水期施工",options=["是","否"], value=st.session_state['inf']['work_water_check'])
        st.session_state['inf']['work_water_check'] = st.checkbox("需要配合斷水期施工", value=st.session_state['inf']['work_water_check'])
        st.markdown("---")
        st.session_state['inf']['work_start_date'] = st.date_input("最佳施工起始日期", value=work_start_date)
        st.session_state['inf']['work_end_date'] = st.date_input("最佳施工結束日期", value=work_end_date)

    with col2:

        # tab1, tab2, tab3, tab4 = st.tabs(["現地近照", "現地遠照", "設計簡圖", "位置圖"])
        tab1, tab2, tab3 = st.tabs(["現地近照", "現地遠照", "設計簡圖"])

        with tab1:
            if  st.session_state.uploaded_file1 is not None:
                uploaded_file1 = st.file_uploader("現地近照", type=["png", "jpg", "jpeg"], key='upload1')
                if uploaded_file1 is not None:
                    st.session_state.uploaded_file1 = uploaded_file1
                    st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)
                else:
                    st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)
            else:
                uploaded_file1 = st.file_uploader("現地近照", type=["png", "jpg", "jpeg"], key='upload1')
                if uploaded_file1 is not None:
                    st.session_state.uploaded_file1 = uploaded_file1
                    st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)

        with tab2:
            if  st.session_state.uploaded_file2 is not None:
                uploaded_file2 = st.file_uploader("現地遠照", type=["png", "jpg", "jpeg"], key='upload2')
                if uploaded_file2 is not None:
                    st.session_state.uploaded_file2 = uploaded_file2
                    st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)
                else:
                    st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)
            else:
                uploaded_file2 = st.file_uploader("現地遠照", type=["png", "jpg", "jpeg"], key='upload2')
                if uploaded_file2 is not None:
                    st.session_state.uploaded_file2 = uploaded_file2
                    st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)

        with tab3:
            if st.session_state.uploaded_file3 is not None:
                uploaded_file3 = st.file_uploader("設計簡圖", type=["png", "jpg", "jpeg"], key='upload3')
                if uploaded_file3 is not None:
                    st.session_state.uploaded_file3 = uploaded_file3
                    st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)
                else:
                    st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)
            else:
                uploaded_file3 = st.file_uploader("設計簡圖", type=["png", "jpg", "jpeg"], key='upload3')
                if uploaded_file3 is not None:
                    st.session_state.uploaded_file3 = uploaded_file3
                    st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)

        # with tab4:
        #     if  st.session_state.uploaded_file4 is not None:
        #         uploaded_file4 = st.file_uploader("位置圖", type=["png", "jpg", "jpeg"], key='upload4')
        #         if uploaded_file4 is not None:
        #             st.session_state.uploaded_file4 = uploaded_file4
        #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)
        #         else:
        #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)
        #     else:
        #         uploaded_file4 = st.file_uploader("位置圖", type=["png", "jpg", "jpeg"], key='upload4')
        #         if uploaded_file4 is not None:
        #             st.session_state.uploaded_file4 = uploaded_file4
        #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)

def render_page2():

    col1,col2=st.columns([6,2])

    with col1:
        if len(st.session_state['coords']) ==0:
            st.subheader("1.點選渠道施作起點")
        elif len(st.session_state['coords']) ==1:
            st.subheader("2.點選渠道施作終點")
        elif len(st.session_state['coords']) == 2:
            st.subheader("3.點選最佳會勘地點")
        else :
            st.subheader("**如果要重新點選請先清空所有座標**")
        col12,col22=st.columns([1,1])
        with col12:
            check_satellite = st.checkbox(":earth_africa: 打開衛星雲圖")
        with col22:
            check_channel= st.checkbox(":bar_chart: 打開渠道圖層")
        # 定義地圖的初始位置和縮放級別
        initial_location = [23.7089, 120.5406]  # 這裡使用台中的經緯度
        initial_zoom = 10

        # 添加點擊事件處理
        def add_marker(folium_map, lat, lon, label):
            folium.Marker(
                location=[lat, lon],
                popup=f"{label}<br>經度: {lon}<br>緯度: {lat}",
                icon=folium.Icon(icon="info-sign"),
            ).add_to(folium_map)

        # 創建一個 Folium 地圖
        map = folium.Map(location=initial_location, zoom_start=initial_zoom)

        if check_satellite:

            folium.raster_layers.WmsTileLayer(
                url='http://maps.nlsc.gov.tw/S_Maps/wms',  # 示例 WMS 服务 URL，请根据需要替换
                layers='PHOTO_MIX',
                name='衛星影像',
                format='image/png',
                # transparent=True,
                # opacity=0.5,
                control=True
            ).add_to(map)

        if check_channel:

            folium.raster_layers.WmsTileLayer(
                url='https://www.iacloud.ia.gov.tw/servergate/sgsgate.ashx/WMS/canal_public',  # 示例 WMS 服务 URL，请根据需要替换
                layers='canal_public',
                name='渠道',
                format='image/png',
                transparent=True,
                opacity=0.6,
                control=True
            ).add_to(map)
            folium.LayerControl().add_to(map)


        # 顯示儲存的標記
        for i, coord in enumerate(st.session_state['coords']):
            add_marker(map, coord['lat'], coord['lon'], label=f"點 {i + 1}")

        # 顯示 Folium 地圖並捕捉點擊事件
        map_data = st_folium(map, width=1000, height=500)

        # 如果有點擊事件，獲取點擊的位置
        if map_data and map_data['last_clicked']:
            lat = map_data['last_clicked']['lat']
            lon = map_data['last_clicked']['lng']
            
            # 轉換坐標系統
            transformer = Transformer.from_crs("epsg:4326", "epsg:3826")
            twd97_x, twd97_y = transformer.transform(lat, lon)

            # 顯示暫存的坐標
            st.write(f"**TWD97 坐標:** X: {twd97_x}, Y: {twd97_y}")

        st.info("如果地圖打開有困難的話，需要將網頁重新開啟，他需要先下載東西下來才能看的到。")


    # 顯示儲存按鈕
    if st.sidebar.button('儲存座標',type='primary') and len(st.session_state['coords']) < 3 :
        st.session_state['coords'].append({'lat': lat, 'lon': lon, 'twd97_x': twd97_x, 'twd97_y': twd97_y})
        st.rerun()

    try:
        twd97_x_input=st.sidebar.number_input('TWD97_X',value=twd97_x)
        twd97_y_input=st.sidebar.number_input('TWD97_Y',value=twd97_y)
    except:
        twd97_x_input=st.sidebar.number_input('TWD97_X')
        twd97_y_input=st.sidebar.number_input('TWD97_Y')
    if st.sidebar.button('輸入座標',type='primary') and len(st.session_state['coords']) < 3 :
        transformer = Transformer.from_crs("epsg:3826", "epsg:4326")
        lat_input, lon_input = transformer.transform(twd97_x_input, twd97_y_input)
        st.session_state['coords'].append({'lat': lat_input, 'lon': lon_input, 'twd97_x': twd97_x_input, 'twd97_y': twd97_y_input})
        st.rerun()

    # 顯示儲存的坐標
    if len(st.session_state['coords']) == 3:
        # st.sidebar.warning("已經選取了兩個位置",icon="⚠️")

        if st.sidebar.button('清空所有坐標',type='primary'):
            st.session_state['coords'] = []  # 清空坐標
            st.rerun()  # 重新運行應用以更新頁面

    # with st.sidebar:
    with col2:

        st.markdown("### :round_pushpin: 座標資訊")

        for i, coord in enumerate(st.session_state['coords']):
            # st.markdown("---")

            if i==0:
                st.markdown(" #### 起點")
            elif i==1:
                st.markdown(" #### 終點")
            elif i==2:
                st.markdown(" #### 會勘點")

            # st.markdown(f"#### 點 {i + 1}")
            st.write(f"X: {coord['twd97_x']}")
            st.write(f"Y: {coord['twd97_y']}")
            st.markdown("---")

def render_page3():

    col1, col2, col3 = st.columns([8, 1, 4])

    with col3:
        st.markdown("#### :small_blue_diamond: 基本單價")
        with st.expander("常見大宗物資"):
            edited_unit_price_df = st.data_editor(get_basic_price_data(), hide_index=True)
        with st.expander("鋼版樁、鋼軌樁"):
            edited_falsework_price_df = st.data_editor(get_falsework_price_data(), hide_index=True)
        
    with col1:
        st.markdown("#### :small_blue_diamond: 工程項目")

        tab_names = ["渠道工程", "版橋工程", "道路工程", "版樁工程", "擋土牆"]
        tabs = st.tabs(tab_names)
        with tabs[0]:
            render_channel_tab(edited_unit_price_df)
        with tabs[1]:
            render_bridge_tab(edited_unit_price_df)
        with tabs[2]:
            render_road_tab(edited_unit_price_df)
        with tabs[3]:
            render_falsework_tab(edited_falsework_price_df)
        with tabs[4]:
            render_wall_tab(edited_unit_price_df)

    with col3:
        with st.expander(":globe_with_meridians: **估算成果**",True):
            coe_other = st.number_input(":star: **雜項費用係數**", min_value=0.0, value=0.1, step=0.05)
            cost_df = get_cost_data(coe_other)
            st.dataframe(cost_df, hide_index=True, use_container_width=True)
            coe = st.number_input(":star: **間接費用係數**", min_value=0.0, value=0.3, step=0.05)
            sum_cost = cost_df['總價'].sum()
            other_cost = round(sum_cost * (1 + coe), -3) - sum_cost
            total_cost = sum_cost + other_cost
            formatted_sum_cost = f"{sum_cost:,.0f}"
            formatted_other_cost = f"{other_cost:,.0f}"
            formatted_total_cost = f"{total_cost:,.0f}"
            st.write(f"直接費用: {formatted_sum_cost} 元")
            st.write(f"間接費用: {formatted_other_cost} 元")
        st.markdown(f"##### :large_orange_diamond: 總費用為 {formatted_total_cost} 元")
        if total_cost != 0:
            with st.sidebar:
                if st.button("工程概要表", type="primary"):
                    report = generate_cost_report(st.session_state['costs'], coe_other,coe)
                    st.text(report)
                    generateXLS(report)
                    
                    # st.json(st.session_state)

def storeMSG(username, email, txt):

    GAS_URL = st.secrets.GAS_URL_NOTIFY

    data = {
        'username': username,
        'email': email,
        'content': txt
    }

    try:
        response = requests.post(GAS_URL, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        # print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return {'success': False, 'error': str(http_err)}
    except Exception as err:
        print(f'Other error occurred: {err}')
        return {'success': False, 'error': str(err)}
    
def session_initialize():

    if 'costs' not in st.session_state:
        st.session_state['costs'] = {
            'open_channel': {'name':'渠道工程','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'bridge': {'name':'版橋工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'wall': {'name':'擋土牆','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'road': {'name':'道路工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'falsework': {'name':'版樁工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0}
        }

    if 'totalcost' not in st.session_state:
        st.session_state['totalcost'] = 0

    if 'inf' not in st.session_state:
        st.session_state['inf'] = {
            'timestamp': datetime.now(),
            'work_place': '雲林縣',
            'work_place2': '斗六市',
            'work_manage':'斗六分處',
            'work_station': '梅林站',
            'work_name': 'OO小給',
            'work_benefit': '20',
            'work_place_water':'處有地',
            'work_place_detail': '已取得並確認妥處',
            'work_water_check':True,
            'work_start_date': date(2024, 1, 1),
            'work_end_date': date(2024, 1, 1),
            'job_length':0,
            'job_cost':0

        }

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'page0'

        # 用來暫存點擊的座標
    if 'coords' not in st.session_state:
        st.session_state['coords'] = []

        # 初始化 session_state 中的文件屬性
    if 'uploaded_file1' not in st.session_state:
        st.session_state.uploaded_file1 = None
    if 'uploaded_file2' not in st.session_state:
        st.session_state.uploaded_file2 = None
    if 'uploaded_file3' not in st.session_state:
        st.session_state.uploaded_file3 = None
    if 'uploaded_file4' not in st.session_state:
        st.session_state.uploaded_file4 = None

def main():

    SYSTEM_VERSION="V1.8.1"

    st.set_page_config(
        page_title="工程估算系統"+SYSTEM_VERSION,
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    session_initialize()

    with st.sidebar:
        st.title(":globe_with_meridians: 工程估算系統 "+SYSTEM_VERSION)
        st.write("這是用於提報計畫時的估算工具")
        st.info("作者:**林宗漢**")
        with st.expander(":clapper: 影片教學"):
            st.video("./video/demo.mp4")
        with st.expander(":mega: 意見回饋"):

            if 'submitted' not in st.session_state:
                st.session_state.submitted = False

            username = st.text_input(":small_blue_diamond: 姓名")
            email = st.text_input(":small_blue_diamond: 電子郵件")
            txt = st.text_area(":small_blue_diamond: 內容")

            if not st.session_state.submitted:
                if st.button("送出",type='primary'):

                    storeMSG(username, email, txt)
                    st.balloons()
                    st.toast("感謝你的意見回復!")
                    st.session_state.submitted = True
                    st.rerun()
            else:
                st.write("**:red[感謝你的意見提供! 如要繼續提供請重新整理]**")
        # st.markdown("---")
        # st.json(st.session_state)
        st.markdown("---")
        st.subheader("選擇頁面")

        if st.button("0.系統操作流程"):
            st.session_state.current_page = 'page0'  
        if st.button("1.工程基本資料"):
            st.session_state.current_page = 'page1'
        if st.button("2.工程施作位置"):
            st.session_state.current_page = 'page2'
        if st.button("3.工程內容概要"):
            st.session_state.current_page = 'page3'
            
        st.markdown("---")
        st.subheader("操作按鈕")

    if st.session_state.current_page == 'page1':
        render_page1()
    elif st.session_state.current_page == 'page2':
        render_page2()
    elif st.session_state.current_page == 'page3':
        render_page3()
    else:
        render_page0()

    # print(st.session_state)

if __name__ == "__main__":
    main()
    # st.sidebar.json(st.session_state)
