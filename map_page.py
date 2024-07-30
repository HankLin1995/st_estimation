import streamlit as st
import folium
from streamlit_folium import st_folium
from pyproj import Transformer

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