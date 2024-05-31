import streamlit as st
import pandas as pd

def render_road_tab(edited_unit_price_df):

    # 初始化 foundation_prices 並更新為從基本單價表獲取的價格

    AC_price=edited_unit_price_df[edited_unit_price_df['材料']=='AC']['單價'].values[0]
    Stone_price=edited_unit_price_df[edited_unit_price_df['材料']=='碎石級配']['單價'].values[0]
    CLSM_price=edited_unit_price_df[edited_unit_price_df['材料']=='CLSM']['單價'].values[0]

    # AC_price = 360
    # Stone_price=790
    # CLSM_price=1460

    road_price_data = {
        'AC':AC_price,
        '再生AC':'310',
        '碎石級配20cm':Stone_price*0.2,
        '碎石級配30cm':Stone_price*0.3,
        'CLSM20cm':CLSM_price*0.2,
        'CLSM30cm':CLSM_price*0.3,
        'AC+碎石級配20cm':AC_price+Stone_price*0.2,
        'AC+碎石級配30cm':AC_price+Stone_price*0.3,
        'AC+CLSM20cm':AC_price+CLSM_price*0.2,
        'AC+CLSM30cm':AC_price+CLSM_price*0.3,
        }
    
    with st.expander(":pushpin: 道路幾何條件:",True):

        # col1,col2=st.columns([1,1])

        # with col1:
        all_keys = list(road_price_data.keys())
        road_type = st.selectbox("選擇材料類別", options=all_keys)
        road_width = st.number_input("輸入施作寬度(m)",value=5, min_value=0,max_value=10)
        road_length = st.number_input("施作長度(m)", min_value=0)
        
        # if road_type != "AC":
        #     road_thickness = st.selectbox("施作厚度(cm)", options=[5,10,15,20,25,30])
        # else:
        #     road_thickness=st.selectbox("施作厚度(cm)", options=[5,10])

        if 'data2' not in st.session_state:
            st.session_state.data2 = []

        if st.button("新增",key="add_road"):
            road_area=road_width*road_length
            # road_volume=road_area*road_thickness/100
            # st.write("A=" , road_area,"m2")
            # st.write("V=" ,road_volume,"m3")

            if road_type in road_price_data:
                unit_price = float(road_price_data[road_type])
                total_price = unit_price * road_area
                st.session_state.data2.append([road_type, unit_price,road_area, total_price])
            else:
                st.error("該材料長度的單價尚未設定，請重新輸入")

    columns = ['材料名稱', '單價 (元/m2)', '施作面積 (m2)', '總複價 (元)']
    df = pd.DataFrame(st.session_state.data2, columns=columns)

    edited_df2 = st.data_editor(df, hide_index=True, num_rows="dynamic")

    st.session_state.data2 = edited_df2.values.tolist()

    if not edited_df2.empty:
        total_cost = edited_df2['總複價 (元)'].sum()
        st.markdown("---")
        st.markdown("### 	:small_red_triangle_down:費用計算")
        st.write(f"道路工程費用: **{total_cost:,.0f}** 元")
        st.write(":warning: 上述費用 :red[未包含]間接費用")
        st.session_state.road_cost=total_cost
