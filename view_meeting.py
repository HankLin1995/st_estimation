"""
會勘地點安排系統
整合自 st_meeting 專案
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import openrouteservice
from datetime import datetime, timedelta
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
import os
from GAS import getOriginData


def initialize_meeting_session():
    """初始化會勘相關的 session state"""
    if 'meeting_current_page' not in st.session_state:
        st.session_state['meeting_current_page'] = 'add_location'
    
    if 'meeting_coords' not in st.session_state:
        st.session_state['meeting_coords'] = []
    
    if 'meeting_show_map' not in st.session_state:
        st.session_state['meeting_show_map'] = True
    
    if 'meeting_routes' not in st.session_state:
        st.session_state['meeting_routes'] = []


def get_duration(start, end):
    """計算兩點之間的行車時間"""
    try:
        API_KEY = st.secrets["OPEN_ROUTE_API_KEY"]
        client = openrouteservice.Client(key=API_KEY)
        routes = client.directions([start, end], profile='driving-car')
        
        if routes and 'routes' in routes and routes['routes']:
            route = routes['routes'][0]
            duration = route['summary']['duration'] / 60  # 轉換為分鐘
            return duration
    except Exception as e:
        st.error(f"計算路程時間失敗: {e}")
        return 0
    

def generate_itinerary(data, start_time_str):
    """生成會勘行程表"""
    start_time = datetime.strptime(start_time_str, '%H:%M')
    itinerary = []

    for i, entry in enumerate(data):
        # 如果不是第一個水路，先加入移動時間
        if i > 0:
            move_start_time = start_time
            move_end_time = move_start_time + timedelta(minutes=entry['移動時間'])
            itinerary.append([f"{move_start_time.strftime('%H:%M')}~{move_end_time.strftime('%H:%M')}", '路程'])
            start_time = move_end_time

        # 生成水路名稱的行程
        waterway_start_time = start_time
        waterway_end_time = waterway_start_time + timedelta(minutes=entry['停留時間'])
        itinerary.append([f"{waterway_start_time.strftime('%H:%M')}~{waterway_end_time.strftime('%H:%M')}", entry['水路名稱']])

        # 更新開始時間為水路停留結束時間
        start_time = waterway_end_time

    return itinerary


def get_coordinates(waterway_name):
    """根據水路名稱獲取座標"""
    for route in st.session_state['meeting_routes']:
        if route["水路名稱"] == waterway_name:
            return route["經度"], route["緯度"]
    return None


def render_add_location():
    """頁面1: 新增會勘地點"""
    st.header("📍 新增會勘地點")
    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("會勘基本資料")
        route_name = st.text_input('水路名稱')
        route_lon = st.text_input("經度")
        route_lat = st.text_input("緯度")

        if st.button("儲存位置", type="primary"):
            if route_lat and route_lon and route_name:
                new_row = {
                    "序號": None,
                    "鄉鎮": None,
                    "水路名稱": route_name,
                    "工作站": None,
                    "水路長度": None,
                    "概估經費": 0,
                    "工程用地": None,
                    "水路用地": None,
                    "最佳施工期": None,
                    "經度": float(route_lon),
                    "緯度": float(route_lat),
                    "停留時間": 20.0,
                    "移動時間": None,
                    "計算時間": None
                }
                st.session_state['meeting_routes'].append(new_row)
                st.session_state['meeting_coords'].append({'lat': float(route_lat), 'lng': float(route_lon)})
                st.success("✅ 位置已儲存!")
                st.rerun()
            else:
                st.error("❌ 請確保水路名稱、經度和緯度都已填寫")
            
    with col2:
        st.subheader("會勘集合地點")

        # 創建地圖
        initial_location = [23.7089, 120.5406]  # 台中
        map_obj = folium.Map(location=initial_location, zoom_start=10)

        # 顯示已儲存的標記
        if st.toggle("顯示紀錄", st.session_state['meeting_show_map']):
            for idx, route in enumerate(st.session_state['meeting_routes']):
                folium.Marker(
                    [route['緯度'], route['經度']], 
                    popup=f"{route['水路名稱']} ({route['經度']}, {route['緯度']})",
                    tooltip=route['水路名稱']
                ).add_to(map_obj)

        # 顯示地圖並捕捉點擊事件
        map_data = st_folium(map_obj, width=1000, height=500)

        # 如果有點擊事件，顯示座標
        if map_data and map_data['last_clicked']:
            lat = round(map_data['last_clicked']['lat'], 6)
            lng = round(map_data['last_clicked']['lng'], 6)
            st.info(f"點擊座標 - 緯度: {lat}, 經度: {lng}")


def render_import_from_gas():
    """頁面2: 從專案管理匯入"""
    st.header("📋 從專案管理匯入")
    
    with st.spinner("載入專案資料中..."):
        df = getOriginData()
    
    if not df.empty:
        st.subheader(f"專案列表（共 {len(df)} 個專案）")
        st.info("💡 勾選 'meeting' 欄位來選擇要會勘的專案")
        
        df_edit = st.data_editor(
            df, 
            hide_index=True, 
            key="gas_editor",
            column_config={
                "meeting": st.column_config.CheckboxColumn(
                    "選取會勘",
                    help="勾選此專案加入會勘清單",
                    default=False,
                ),
                "id": st.column_config.NumberColumn("專案ID", disabled=True),
                "inf.work_name": st.column_config.TextColumn("水路名稱", width="medium"),
                "inf.work_place2": st.column_config.TextColumn("鄉鎮", width="small"),
                "inf.work_station": st.column_config.TextColumn("工作站", width="small"),
                "inf.job_length": st.column_config.NumberColumn("長度(m)", format="%.0f"),
                "inf.job_cost": st.column_config.NumberColumn("經費(元)", format="%.0f"),
                "coords.2.lat": st.column_config.NumberColumn("緯度", format="%.6f"),
                "coords.2.lon": st.column_config.NumberColumn("經度", format="%.6f"),
            }
        )
        
        df_meeting = df_edit[df_edit['meeting']]
        
        if len(df_meeting) > 0:
            st.markdown("---")
            st.subheader(f"已選取 {len(df_meeting)} 個會勘地點")
            
            df_result = []
            
            for index, row in df_meeting.iterrows():
                st.write(f"✓ **{row['inf.work_name']}** - E: {row['coords.2.lon']:.6f}, N: {row['coords.2.lat']:.6f}")
                
                # 最佳施工期
                work_start_date_str = str(row['inf.work_start_date'])
                work_end_date_str = str(row['inf.work_end_date'])
                
                try:
                    work_start_date = datetime.strptime(work_start_date_str, '%Y-%m-%d')
                    work_end_date = datetime.strptime(work_end_date_str, '%Y-%m-%d')
                    work_date_range = f"{work_start_date.strftime('%Y/%m')} ~ {work_end_date.strftime('%Y/%m')}"
                except:
                    work_date_range = "未設定"

                new_row = {
                    "序號": None,
                    "鄉鎮": row['inf.work_place2'],
                    "水路名稱": row['inf.work_name'],
                    "工作站": row['inf.work_station'],
                    "水路長度": row['inf.job_length'],
                    "概估經費": row['inf.job_cost'],
                    "工程用地": row['inf.work_place_water'],
                    "水路用地": row['inf.work_place_detail'], 
                    "最佳施工期": work_date_range,
                    "經度": float(row['coords.2.lon']),
                    "緯度": float(row['coords.2.lat']),
                    "停留時間": 20.0,
                    "移動時間": None,
                    "計算時間": None
                }
                df_result.append(new_row)

            if st.button("📥 匯入選取的地點", type="primary", use_container_width=True):
                st.session_state['meeting_routes'] = df_result
                st.success(f"✅ 已匯入 {len(df_result)} 個會勘地點")
                st.rerun()
        else:
            st.info("請勾選要會勘的專案")
    else:
        st.warning("⚠️ 無法獲取專案資料，請確認後端服務是否正常運作")


def render_arrange_meeting():
    """頁面3: 安排會勘地點"""
    st.header("🗺️ 安排會勘地點")
    
    if not st.session_state['meeting_routes']:
        st.warning("⚠️ 尚無會勘地點，請先新增或匯入")
        return
    
    # 會勘日期時間
    col1, col2 = st.columns(2)
    with col1:
        meet_date = st.date_input('會勘日期')
    with col2:
        meet_time = st.time_input('會勘時間')

    start_time_datetime = meet_time
    sorted_data = st.session_state['meeting_routes']

    # 自動排序
    if any(item['序號'] is None for item in sorted_data):
        sorted_data = sorted(st.session_state['meeting_routes'], key=lambda x: x["經度"])
        for index, item in enumerate(sorted_data):
            item["序號"] = index + 1

    # 編輯會勘清單
    st.subheader("會勘清單")
    edited_data = st.data_editor(sorted_data, key="meeting_editor", hide_index=True)
    plot_data = sorted(edited_data, key=lambda x: x["序號"]) 

    # 計算路程時間
    if st.button("🚗 計算路程時間"):
        df = pd.DataFrame(plot_data)
        coordinates = df[['經度', '緯度']].values.tolist()
        paired_coordinates = [[coordinates[i], coordinates[i+1]] for i in range(len(coordinates) - 1)]

        with st.spinner("計算中..."):
            for i, (start, end) in enumerate(paired_coordinates):
                api_time = get_duration(start, end)
                df.at[i+1, '計算時間'] = api_time
                
                # 設定移動時間間隔
                intervals = [5, 10, 15, 20, 25, 30]
                move_time = next((t for t in intervals if api_time < t), 30)
                df.at[i + 1, '移動時間'] = move_time

            df.at[0, '移動時間'] = 0
            df.at[0, '計算時間'] = 0

            st.session_state['meeting_routes'] = df.to_dict('records')
            st.success("✅ 路程時間計算完成")
            st.rerun()

    # 生成行程表
    if st.button("📄 生成行程表 Excel"):
        start_time = start_time_datetime.strftime('%H:%M')
        my_list = generate_itinerary(st.session_state['meeting_routes'], start_time)

        # 載入 Excel 模板
        template_path = './template/ARRANGE.xlsx'
        if not os.path.exists(template_path):
            st.error("❌ 找不到 Excel 模板檔案")
            return

        wb = load_workbook(template_path)
        ws = wb.active
        ws.cell(row=2, column=4, value=meet_date.strftime("%Y-%m-%d"))

        last_row = 3
        j = 0
        df_data = st.session_state['meeting_routes']

        for item in my_list:
            target_name = item[1]
            list_filter = [item for item in df_data if item.get('水路名稱') == target_name]

            if len(list_filter) > 0:
                dict_filter = list_filter[0]
                serial_number = item[0]
                waterway_name = item[1]
                coordinates = get_coordinates(waterway_name)

                if coordinates:
                    j += 1
                    longitude, latitude = coordinates
                    url = f"https://www.google.com/maps/place/{latitude},{longitude}"

                    # 填入資料
                    ws.cell(row=last_row + 1, column=1, value=j)
                    ws.cell(row=last_row + 1, column=3, value=dict_filter['鄉鎮'])
                    ws.cell(row=last_row + 1, column=4, value=waterway_name)
                    ws.cell(row=last_row + 1, column=5, value=dict_filter['工作站'])
                    ws.cell(row=last_row + 1, column=6, value=dict_filter['水路長度'])
                    ws.cell(row=last_row + 1, column=7, value=dict_filter['概估經費']/1000)
                    ws.cell(row=last_row + 1, column=8, value=dict_filter['水路用地'])
                    ws.cell(row=last_row + 1, column=9, value=dict_filter['工程用地'])
                    ws.cell(row=last_row + 1, column=10, value=dict_filter['最佳施工期'])
                    ws.cell(row=last_row + 1, column=11, value=serial_number)
                    ws.cell(row=last_row + 2, column=12, value=longitude)
                    ws.cell(row=last_row + 2, column=13, value=latitude)
                    
                    cell = ws.cell(row=last_row + 1, column=12, value=url)
                    cell.hyperlink = url
                    cell.style = "Hyperlink"
                    cell.font = Font(size=18, color="3399FF", underline="single")
                    
                    ws.merge_cells(start_row=last_row + 1, start_column=12, end_row=last_row + 1, end_column=13)
                    ws.cell(row=last_row + 1, column=12).alignment = Alignment(vertical='center', horizontal='center')
                    ws.cell(row=last_row + 1, column=12).font = Font(size=12, color="3399FF", underline="single")
                    
                    last_row += 2  

        ws.print_area = 'A1:N' + str(last_row)

        # 儲存並提供下載
        output_file = f'會勘行程表_{meet_date.strftime("%Y%m%d")}.xlsx'
        wb.save(output_file)
        
        with open(output_file, 'rb') as f:
            bytes_data = f.read()
        
        st.download_button(
            label='📥 下載行程表',
            data=bytes_data,
            file_name=output_file,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type='primary'
        )
        os.remove(output_file)

    # 地圖顯示
    st.markdown("---")
    st.subheader("會勘地圖")
    
    is_show_path = st.checkbox("顯示路徑", True)
    map_data = folium.Map(location=[23.7089, 120.5406], zoom_start=11)

    if is_show_path:
        path = [(item["緯度"], item["經度"]) for item in plot_data]
        folium.PolyLine(path, color="blue", weight=2.5, opacity=1).add_to(map_data)

        for index, item in enumerate(plot_data):
            folium.Marker(
                location=[item["緯度"], item["經度"]],
                icon=folium.DivIcon(
                    html=f"""
                        <div style="position: relative; top: -10px; left: -10px;">
                            <svg>
                                <circle cx="10" cy="10" r="10" fill="red" />
                                <text x="10" y="15" fill="white" text-anchor="middle" font-size="16">{item['序號']}</text>
                            </svg>
                        </div>
                    """
                )
            ).add_to(map_data)
    else:
        for item in sorted_data:
            folium.Marker(
                [item['緯度'], item['經度']], 
                popup=f"{item['水路名稱']} ({item['經度']}, {item['緯度']})",
                tooltip=item['水路名稱'],
                icon=folium.Icon(color='green', prefix='glyphicon')
            ).add_to(map_data)

    # 加入鄉鎮圖層
    folium.raster_layers.WmsTileLayer(
        url='http://maps.nlsc.gov.tw/S_Maps/wms',
        layers='TOWN',
        name='鄉鎮市',
        format='image/png',
        transparent=True,
        opacity=0.5,
        control=True
    ).add_to(map_data)

    folium.LayerControl().add_to(map_data)
    st_folium(map_data, width=800, height=400)


# 主程式
initialize_meeting_session()

st.title("🌐 會勘地點安排系統")

# 側邊欄導航
with st.sidebar:
    st.header("📋 功能選單")
    
    if st.button("📍 新增會勘地點", use_container_width=True):
        st.session_state['meeting_current_page'] = 'add_location'
        st.rerun()
    
    if st.button("📋 從專案管理匯入", use_container_width=True):
        st.session_state['meeting_current_page'] = 'import_gas'
        st.rerun()
    
    if st.button("🗺️ 安排會勘地點", use_container_width=True):
        st.session_state['meeting_current_page'] = 'arrange'
        st.rerun()
    
    st.markdown("---")
    st.info(f"📊 目前共有 **{len(st.session_state['meeting_routes'])}** 個會勘地點")
    
    if st.button("🗑️ 清除所有地點", type="secondary"):
        st.session_state['meeting_routes'] = []
        st.session_state['meeting_coords'] = []
        st.success("已清除所有地點")
        st.rerun()

# 頁面路由
if st.session_state['meeting_current_page'] == 'add_location':
    render_add_location()
elif st.session_state['meeting_current_page'] == 'import_gas':
    render_import_from_gas()
elif st.session_state['meeting_current_page'] == 'arrange':
    render_arrange_meeting()
