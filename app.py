import streamlit as st
import pandas as pd
from tabs import render_falsework_tab, render_channel_tab, render_bridge_tab, render_road_tab, render_wall_tab
import openpyxl
import os
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import datetime
import requests

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

def get_cost_data():
    cost_data = []
    for key, item in st.session_state['costs'].items():
        cost_data.append({
            '項目': item['name'],
            '總價': item['total_cost'],
            '單位': '元'
        })

    return pd.DataFrame(cost_data)

def generate_cost_report(costs, indirect_coefficient=0.4):
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

    indirect_cost = round(total_direct_cost * (1+indirect_coefficient),-3)-total_direct_cost
    total_cost = total_direct_cost + indirect_cost

    report.append(f"\n直接工程費 = {total_direct_cost:,.0f}元")
    report.append(f"間接工程費(含雜項) = 直接工程費 * {indirect_coefficient} = {indirect_cost:,.0f}元")
    report.append(f"\n總工程費 = {total_cost:,.0f}元")

    return "\n".join(report)

def generateXLS(report):


    if len(st.session_state['coords']) == 2:
        # Extract the coordinates
        X1 = st.session_state['coords'][0]['twd97_x']
        Y1 = st.session_state['coords'][0]['twd97_y']
        X2 = st.session_state['coords'][1]['twd97_x']
        Y2 = st.session_state['coords'][1]['twd97_y']


    workbook = openpyxl.load_workbook('./template/PLAN.xlsx')
    sheet = workbook["概要表"]

    sheet.cell(row=3, column=8).value = report
    sheet.cell(row=16,column=4).value=X1
    sheet.cell(row=17,column=4).value=Y1
    sheet.cell(row=18,column=4).value=X2
    sheet.cell(row=19,column=4).value=Y2

    output_file = 'example.xlsx'
    workbook.save(output_file)
    with open(output_file, 'rb') as f:
        bytes_data = f.read()
    st.sidebar.download_button(label='計算成果下載', data=bytes_data, file_name=output_file, type='primary')
    os.remove(output_file)

def render_page0():
    st.header(":dart:操作說明")

    st.markdown("""
                
    ##### 報表生成流程:
                
    :one: 填寫基本資料
                
    :two: 點選施作位置
                
    :three: 填寫工程內容概要
                
    :four: 出現金額後點選左側操作按鈕"工程概要表"即可輸出 
    """)
    with st.expander(":mag: 工程內容填寫教學"):

        st.markdown("""

        **渠道工程、版橋工程、擋土牆**
            
            1. 選擇工程項目
            2. 填寫幾何條件
            3. 生成材料計算表
            4. 如要調整可以直接修改材料計算表內容
        
        **道路工程、版樁工程**

            1. 選擇材料類別
            2. 填寫幾何條件
            3. 點選新增加入工程統計表
            4. 如要調整可以於統計表進行刪除
                
        """)


    with st.expander(":mega: 給開發者的話(意見提供、問題回饋)"):

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

    st.session_state.current_page = 'render_page0'

def render_page1():

    st.subheader("工程基本資料")

    col1,col2=st.columns([1,1])

    with col1:

        st.text_input("工程地點")
        st.text_input("OO分處OO站")
        st.text_input("水路名稱")
        st.text_input("工程效益")
        st.radio("工程用地",options=["已取得並確認妥處","尚未取得或尚未妥處"])
        st.checkbox("是否需要配合斷水期施工")

    with col2:
        # Handling the upload of the first image
        uploaded_file1 = st.file_uploader("現地近照", type=["png", "jpg", "jpeg"], key='upload1')
        if uploaded_file1 is not None:
            st.session_state.uploaded_file1 = uploaded_file1
        
        if 'uploaded_file1' in st.session_state:
            st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)
        
        st.markdown("---")
        
        # Handling the upload of the second image
        uploaded_file2 = st.file_uploader("現地遠照", type=["png", "jpg", "jpeg"], key='upload2')
        if uploaded_file2 is not None:
            st.session_state.uploaded_file2 = uploaded_file2
        
        if 'uploaded_file2' in st.session_state:
            st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)


def render_page2():

    st.subheader("點選渠道施作位置")

    # 定義地圖的初始位置和縮放級別
    initial_location = [23.7089, 120.5406]  # 這裡使用台中的經緯度
    initial_zoom = 12

    # 用來暫存點擊的座標
    if 'coords' not in st.session_state:
        st.session_state['coords'] = []

    # 添加點擊事件處理
    def add_marker(folium_map, lat, lon, label):
        folium.Marker(
            location=[lat, lon],
            popup=f"{label}<br>經度: {lon}<br>緯度: {lat}",
            icon=folium.Icon(icon="info-sign"),
        ).add_to(folium_map)

    # 創建一個 Folium 地圖
    map = folium.Map(location=initial_location, zoom_start=initial_zoom)

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

    # 顯示儲存按鈕
    if st.sidebar.button('儲存目前位置',type='primary') and len(st.session_state['coords']) < 2 :
        st.session_state['coords'].append({'lat': lat, 'lon': lon, 'twd97_x': twd97_x, 'twd97_y': twd97_y})
        st.rerun()

    # 顯示儲存的坐標
    if len(st.session_state['coords']) == 2:
        st.sidebar.warning("已經選取了兩個位置",icon="⚠️")

        if st.sidebar.button('清空所有坐標'):
            st.session_state['coords'] = []  # 清空坐標
            st.rerun()  # 重新運行應用以更新頁面
    #     with st.sidebar:
            # for i, coord in enumerate(st.session_state['coords']):
                # st.markdown("---")
                # st.markdown(f"### 點 {i + 1} - TWD97 坐標")
                # st.write(f"X: {coord['twd97_x']}")
                # st.write(f"Y: {coord['twd97_y']}")
            # if len(st.session_state['coords']) == 2:
            #     st.success("已經選取了兩個位置")

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
        with st.expander(":globe_with_meridians: **估算成果**"):
            cost_df = get_cost_data()
            st.dataframe(cost_df, hide_index=True, use_container_width=True)
            coe = st.number_input(":star: **間接費用係數(含雜項)**", min_value=0.0, value=0.4, step=0.05)
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
                    report = generate_cost_report(st.session_state['costs'], coe)
                    st.text(report)
                    generateXLS(report)

def storeMSG(username, email, txt):

    GAS_URL = st.secrets.GAS_URL

    data = {
        'username': username,
        'email': email,
        'content': txt
    }

    try:
        response = requests.post(GAS_URL, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return {'success': False, 'error': str(http_err)}
    except Exception as err:
        print(f'Other error occurred: {err}')
        return {'success': False, 'error': str(err)}


def main():
    st.set_page_config(
        page_title="工程估算系統",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if 'costs' not in st.session_state:
        st.session_state['costs'] = {
            'open_channel': {'name':'渠道工程','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'bridge': {'name':'版橋工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'wall': {'name':'擋土牆','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'road': {'name':'道路工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'falsework': {'name':'版樁工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0}
        }


    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'page0'

    with st.sidebar:
        st.title(":globe_with_meridians: 工程估算系統 V1.2")
        st.write("這是用於提報計畫時的估算工具")
        st.info("作者:**林宗漢**")
        # st.markdown("---")
        # st.json(st.session_state)
        st.markdown("---")
        st.subheader("選擇頁面")
        if st.button("工程基本資料"):
            st.session_state.current_page = 'page1'
        if st.button("工程施作位置"):
            st.session_state.current_page = 'page2'
        if st.button("工程內容概要"):
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

if __name__ == "__main__":
    main()
