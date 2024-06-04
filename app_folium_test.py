import streamlit as st
import folium
from streamlit_folium import st_folium
from pyproj import Transformer

# 設定頁面標題
st.title("點選渠道施作位置")

# 設定側邊欄標題
with st.sidebar:
    st.title(":world_map: 工程施作位置")
    st.write("這是用於提報計畫時的地圖工具")
    st.info("作者:**林宗漢**")

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
map_data = st_folium(map, width=700, height=500)

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
    if st.sidebar.button('儲存目前位置') and len(st.session_state['coords']) < 2:
        st.session_state['coords'].append({'lat': lat, 'lon': lon, 'twd97_x': twd97_x, 'twd97_y': twd97_y})
        st.rerun()

# 顯示儲存的坐標
if st.session_state['coords']:
    with st.sidebar:
        for i, coord in enumerate(st.session_state['coords']):
            st.markdown("---")
            st.markdown(f"### 點 {i + 1} - TWD97 坐標")
            st.write(f"X: {coord['twd97_x']}")
            st.write(f"Y: {coord['twd97_y']}")
        if len(st.session_state['coords']) == 2:
            st.success("已經選取了兩個位置")
