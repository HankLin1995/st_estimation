import streamlit as st
import folium
from streamlit_folium import st_folium
from pyproj import Transformer

# 設定頁面標題
# st.set_page_config(layout="wide")
st.title("點選渠道施作位置")

# 設定側邊欄標題
with st.sidebar:
    st.title(":world_map: 工程施作位置")
    st.write("這是用於提報計畫時的地圖工具")
    st.info("作者:**林宗漢**")

# 定義地圖的初始位置和縮放級別
initial_location = [23.7089, 120.5406]  # 這裡使用台中的經緯度
initial_zoom = 12

# 創建一個 Folium 地圖
map = folium.Map(location=initial_location, zoom_start=initial_zoom)

# 添加點擊事件處理
def add_marker(lat, lon, label):
    # folium.Marker(
    #     location=[lat, lon],
    #     popup=f"{label}<br>經度: {lon}<br>緯度: {lat}"
        
    #     # icon=folium.Icon(icon="info-sign")
    # )
    folium.Marker(
        location=[lat, lon],
        popup="這裡是台北",
        icon=folium.Icon(icon="info-sign"),
    ).add_to(map)
    # print("jhel;")

# 用來暫存點擊的座標
temp_coords = st.session_state.get('temp_coords', {})
coords = st.session_state.get('coords', [])

# 顯示 Folium 地圖並捕捉點擊事件
map_data = st_folium(map, width=700, height=500)

# 如果有點擊事件，獲取點擊的位置
if map_data and map_data['last_clicked']:
    lat = map_data['last_clicked']['lat']
    lon = map_data['last_clicked']['lng']
    temp_coords = {'lat': lat, 'lon': lon}
    st.session_state['temp_coords'] = temp_coords
    add_marker(lat, lon, label="暫存點")

    # st.write('經度:', temp_coords['lon'],",緯度:",temp_coords['lat'])
    transformer = Transformer.from_crs("epsg:4326", "epsg:3826")
    twd97_x, twd97_y = transformer.transform(temp_coords['lat'], temp_coords['lon'])

    st.write('**TWD97 坐標:** X:', twd97_x, ",Y:",twd97_y)

# 顯示暫存的坐標
if temp_coords:
    with st.sidebar:

        if len(coords) < 2:
            if st.button('儲存目前位置'):
                coords.append({'lat': temp_coords['lat'], 'lon': temp_coords['lon'], 'twd97_x': twd97_x, 'twd97_y': twd97_y})
                st.session_state['coords'] = coords
                st.session_state['temp_coords'] = {}

# 顯示儲存的坐標
if coords:
    with st.sidebar:
        for i, coord in enumerate(coords):

            st.markdown("---")
            st.markdown(f"### 點 {i + 1} - TWD97 坐標")
            st.write('X:', coord['twd97_x'])
            st.write('Y:', coord['twd97_y'])

        if len(coords) == 2:
            st.success("已經選取了兩個位置")

# 在地圖上添加儲存的標記
for i, coord in enumerate(coords):
    add_marker(coord['lat'], coord['lon'], label=f"點 {i + 1}")