import streamlit as st
import pandas as pd
from tabs import render_falsework_tab, render_channel_tab, render_bridge_tab, render_road_tab, render_wall_tab
import datetime
import requests
import json
from myImage import insert_image
from openpyxl.drawing.image import Image as OpenpyxlImage
# from json_test import st_to_json
from datetime import datetime,date
import openpyxl
from openpyxl.drawing.image import Image
import os,io
import uuid
from api_client import APIClient

# Initialize API Client
api_client = APIClient()
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

        output_file = 'example.xlsx'

        workbook.save(output_file)
        with open(output_file, 'rb') as f:
            bytes_data = f.read()
        btn=st.sidebar.download_button(label='計算成果下載', data=bytes_data, file_name=output_file, type='primary')
        os.remove(output_file)
        print("HI")
        savedata()

def savedata():
    """Save project and coordinates data to backend"""
    try:
        with st.sidebar:
            with st.spinner("...資料儲存中..."):
                # Check backend health first
                if not api_client.health_check():
                    st.error("❌ 無法連接到後端伺服器，請確認伺服器是否正在運行")
                    return
                
                # Prepare project data (不再需要 project_id)
                # 處理日期格式 - 加上時間部分以符合 datetime 格式
                work_start_date = st.session_state['inf'].get('work_start_date')
                work_end_date = st.session_state['inf'].get('work_end_date')
                
                # 將 date 轉換為 datetime 格式的 ISO 字串
                start_date_str = None
                if work_start_date:
                    if isinstance(work_start_date, date) and not isinstance(work_start_date, datetime):
                        # 如果是 date，轉換為 datetime（加上 00:00:00）
                        start_date_str = datetime.combine(work_start_date, datetime.min.time()).isoformat()
                    else:
                        start_date_str = work_start_date.isoformat()
                
                end_date_str = None
                if work_end_date:
                    if isinstance(work_end_date, date) and not isinstance(work_end_date, datetime):
                        # 如果是 date，轉換為 datetime（加上 00:00:00）
                        end_date_str = datetime.combine(work_end_date, datetime.min.time()).isoformat()
                    else:
                        end_date_str = work_end_date.isoformat()
                
                project_data = {
                    "work_place": st.session_state['inf'].get('work_place', ''),
                    "work_place2": st.session_state['inf'].get('work_place2', ''),
                    "work_manage": st.session_state['inf'].get('work_manage', ''),
                    "work_station": st.session_state['inf'].get('work_station', ''),
                    "work_name": st.session_state['inf'].get('work_name', ''),
                    "work_benefit": st.session_state['inf'].get('work_benefit', ''),
                    "waterway_type": st.session_state['inf'].get('waterway_type', ''),  # 新增：水路分類
                    "benefit_description": st.session_state['inf'].get('benefit_description', ''),  # 新增：效益說明
                    "work_place_water": st.session_state['inf'].get('work_place_water', ''),
                    "work_place_detail": st.session_state['inf'].get('work_place_detail', ''),
                    "work_water_check": st.session_state['inf'].get('work_water_check') == "是",
                    "work_start_date": start_date_str,
                    "work_end_date": end_date_str,
                    "job_length": st.session_state['inf'].get('job_length', 0),
                    "job_cost": st.session_state['inf'].get('job_cost', 0)
                }
                
                # Save project
                project_result = api_client.create_project(project_data)
                
                if project_result:
                    # 儲存後端返回的 integer id
                    project_id = project_result['id']
                    st.session_state['inf']['backend_project_id'] = project_id
                    
                    st.success(f"✅ 專案已建立 (ID: {project_id})")
                    
                    # Save coordinates if available
                    if 'coords' in st.session_state and len(st.session_state['coords']) > 0:
                        saved_coords = []
                        for idx, coord in enumerate(st.session_state['coords']):
                            coord_data = {
                                "project_id": project_id,  # 使用後端返回的 integer id
                                "order": idx + 1,
                                "twd97_x": coord.get('twd97_x', 0),
                                "twd97_y": coord.get('twd97_y', 0),
                                "wgs84_lat": coord.get('wgs84_lat'),  # 使用新欄位名稱
                                "wgs84_lng": coord.get('wgs84_lng')   # 使用新欄位名稱
                            }
                            coord_result = api_client.create_coordinate(coord_data)
                            if coord_result:
                                saved_coords.append(coord_result)
                        
                        if len(saved_coords) == len(st.session_state['coords']):
                            st.success(f"✅ 已儲存 {len(saved_coords)} 個座標點")
                        else:
                            st.warning(f"⚠️ 座標儲存不完整：{len(saved_coords)}/{len(st.session_state['coords'])}")
                    
                    # Save images if available (新增圖片儲存功能)
                    saved_images = 0
                    image_mapping = {
                        'uploaded_file1': '近照',    # 設計圖
                        'uploaded_file2': '遠照',  # 近照
                        'uploaded_file3': '設計圖'        # 遠照
                    }
                    
                    for file_key, image_type in image_mapping.items():
                        if hasattr(st.session_state, file_key) and getattr(st.session_state, file_key) is not None:
                            uploaded_file = getattr(st.session_state, file_key)
                            image_data = {
                                "project_id": project_id,
                                "image_type": image_type,
                                "file_name": uploaded_file.name,
                                "file_path": f"/uploads/{project_id}/{uploaded_file.name}",
                                "mime_type": uploaded_file.type if hasattr(uploaded_file, 'type') else "image/jpeg",
                                "file_size": uploaded_file.size if hasattr(uploaded_file, 'size') else 0
                            }
                            image_result = api_client.create_image(image_data)
                            if image_result:
                                saved_images += 1
                    
                    if saved_images > 0:
                        st.success(f"✅ 已儲存 {saved_images} 張圖片")
                    
                    st.success("✅ 所有資料儲存完成!")
                else:
                    st.error("❌ 專案建立失敗")
                    
    except Exception as e:
        st.error(f"儲存過程發生錯誤: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

#===== 以下為版面 =====

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
        st.dataframe(cost_df, hide_index=True, width="stretch")
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