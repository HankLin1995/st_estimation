import streamlit as st
import pandas as pd

def render_retaining_wall_tab(edited_unit_price_df):

    # st.title("擋土工程費用計算")
    # 初始化材料數據
    foundation_prices = {
        '鋼板樁': {4.5: 2310, 6: 2910, 7: 3420, 9: 3750, 13: 4410},
        '鋼軌樁': {4: 1620, 6: 1800, 7: 1950, 10: 2850, 12: 3400}
    }

    # 用戶輸入區域
    # st.write(":blue[:point_down: 請填寫材料類別、材料長度、施作長度]")
    
    material_type = st.selectbox("選擇材料類別", options=["鋼板樁", "鋼軌樁"])

    if material_type=="鋼板樁":
        material_length=st.selectbox("請輸入材料長度(M)", options=["4.5", "6","7","9","13"])
    else:
        material_length=st.selectbox("請輸入材料長度(M)", options=["4", "6","7","10","12"])

    construction_length = st.number_input("輸入施作長度", min_value=0, step=1)
    
    if 'data' not in st.session_state:
        st.session_state.data = []

    if st.button("新增"):
        # 將 material_length 轉換為浮點數
        material_length_float = float(material_length)
        if material_length_float in foundation_prices[material_type]:
            unit_price = foundation_prices[material_type][material_length_float]
            total_price = unit_price * construction_length
            st.session_state.data.append([material_type, material_length_float, unit_price, construction_length, total_price])
        else:
            st.error("該材料長度的單價尚未設定，請重新輸入")

    # 建立和顯示DataFrame
    columns = ['材料類別', '材料長度 (m)', '單價 (元/米)', '施作長度 (米)', '總複價 (元)']
    df = pd.DataFrame(st.session_state.data, columns=columns)

    # 顯示 DataFrame
    edited_df = st.data_editor(df, hide_index=True, num_rows="dynamic")

    # 確保更新 session_state.data
    st.session_state.data = edited_df.values.tolist()

    # 計算總費用
    if not edited_df.empty:
        total_cost = edited_df['總複價 (元)'].sum()
        st.markdown("---")
        # st.write(f"### 總費用")
        st.write(f"擋土工程費用: **{total_cost:,.0f}** 元")
        st.write(":warning: 上述費用 :red[未包含]間接費用")
