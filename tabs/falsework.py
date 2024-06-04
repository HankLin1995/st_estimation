import streamlit as st
import pandas as pd

def render_falsework_tab(edited_falsework_price_df):

    # 初始化 foundation_prices 並更新為從基本單價表獲取的價格
    foundation_prices = {
        '鋼板樁': {4.5: 2310, 6: 2910, 7: 3420, 9: 3750, 13: 4410},
        '鋼軌樁': {4: 1620, 6: 1800, 7: 1950, 10: 2850, 12: 3400}
    }

    # 更新 foundation_prices 中的單價
    for index, row in edited_falsework_price_df.iterrows():
        material = row['材料']
        if '鋼板樁' in material:
            length = float(material.replace('鋼板樁L=', '').replace('M', ''))
            foundation_prices['鋼板樁'][length] = row['單價']
        elif '鋼軌樁' in material:
            length = float(material.replace('鋼軌樁L=', '').replace('M', ''))
            foundation_prices['鋼軌樁'][length] = row['單價']

    with st.expander(":pushpin: 幾何條件:",True):

        col1,col2=st.columns([1,1])

        with col1:

            material_type = st.selectbox("選擇材料類別", options=["鋼板樁", "鋼軌樁"])

            if material_type == "鋼板樁":

                material_length = st.selectbox("請輸入材料長度(M)", options=["4.5", "6", "7", "9", "13"])
            else:
                material_length = st.selectbox("請輸入材料長度(M)", options=["4", "6", "7", "10", "12"])

            construction_length = st.number_input("輸入施作長度", min_value=0, step=1)

        with col2:
            if material_type == "鋼板樁":
                st.image("photos/steel_sheet_pile.png", caption="鋼板樁示意圖")
            else:
                st.image("photos/steel_rail_pile.jpg", caption="鋼軌樁示意圖")

        if 'data' not in st.session_state:
            st.session_state.data = []

        if st.button("新增"):
            material_length_float = float(material_length)
            if material_length_float in foundation_prices[material_type]:
                unit_price = foundation_prices[material_type][material_length_float]
                total_price = unit_price * construction_length
                st.session_state.data.append([material_type, material_length_float, unit_price, construction_length, total_price])
            else:
                st.error("該材料長度的單價尚未設定，請重新輸入")

    columns = ['材料類別', '材料長度 (m)', '單價 (元/米)', '施作長度 (米)', '總複價 (元)']
    df = pd.DataFrame(st.session_state.data, columns=columns)

    edited_df = st.data_editor(df, hide_index=True, num_rows="dynamic")

    st.session_state.data = edited_df.values.tolist()

    if not edited_df.empty:
        total_cost = edited_df['總複價 (元)'].sum()
        st.markdown("---")
        st.markdown("##### 	:small_red_triangle_down:費用計算")
        st.write(f"擋土工程費用: **{total_cost:,.0f}** 元")
        st.write(":warning: 上述費用 :red[未包含]間接費用")
        # st.session_state.falsework_cost=total_cost
        st.session_state['costs']['falsework']['unit_cost'] = int(total_cost)
        st.session_state['costs']['falsework']['quantity'] = 1
        st.session_state['costs']['falsework']['total_cost'] = int(total_cost)

