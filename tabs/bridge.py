import streamlit as st
import pandas as pd
import numpy as np

def calculate_materials_bridge(width, length):
    bridge_thickness = get_wall_thickness_bridge(width)

    volume_140_concrete = 0
    volume_210_concrete = bridge_thickness * (width * length)
    weight_steel = interpolate_rebar_amount_bridge(width) * length
    area_formwork_A = 0
    area_formwork_B = 0
    if width >= 1.5:
        area_formwork_A = 2 * (width + length) * bridge_thickness
    else:
        area_formwork_B = 2 * (width + length) * bridge_thickness

    return volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B

def get_wall_thickness_bridge(width):
    if width < 1.0:
        return 0.2
    elif 1.0 <= width < 2.0:
        return 0.25
    elif 2.0 <= width < 3.0:
        return 0.3
    elif 3.0 <= width < 4.0:
        return 0.35
    elif 4.0 <= width <= 5.0:
        return 0.4
    else:
        return 0.45

def interpolate_rebar_amount_bridge(width):
    widths = [0, 1.0, 2.0, 3.0, 4.0, 5.0]
    rebar_amounts = [20, 30, 40, 50, 60, 70]

    if width <= 0:
        return rebar_amounts[0]
    elif width >= 5.0:
        return rebar_amounts[-1]
    else:
        return np.interp(width, widths, rebar_amounts)
    
def input_and_update_state(label, session_key, default_value, min_value=None, max_value=None, step=None):
    if session_key not in st.session_state:
        st.session_state[session_key] = default_value  # 預設值

    value = st.number_input(label, min_value=min_value, max_value=max_value, value=st.session_state.get(session_key), step=step)
    st.session_state[session_key] = value  # 更新值
    return value

def render_bridge_tab(edited_unit_price_df):
    with st.expander(":pushpin: 版橋幾何條件", expanded=True):
        col1, col2 = st.columns([1, 1])

        with col1:
            # 寬度W (m)
            width = input_and_update_state("寬度W (m)", "bridge_width", 1.0, min_value=0.0, max_value=5.0, step=0.1)

            # 每座長度L (m)
            length = input_and_update_state("每座長度L (m)", "bridge_length", 4.0, min_value=4.0, max_value=6.0, step=0.1)

            # 數量 (座)
            cnt = input_and_update_state("數量 (座)", "bridge_cnt", 0.0, min_value=0.0, step=0.1)

            # 推估厚度T
            thickness = get_wall_thickness_bridge(width)
            st.write("*推估厚度T: ", thickness, " m")
        with col2:
            st.image('photos/images_bridge.jpg', caption='版橋範例')

        volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B = calculate_materials_bridge(width, length)

        material_data = {
            '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板', '其他'],
            '數量': [volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B, 0],
            '單位': ['m3', 'm3', 'kg', 'm2', 'm2', '元']
        }
        material_df = pd.DataFrame(material_data)

    with st.expander(":signal_strength: 材料計算表(每座)"):
        edited_material_df = st.data_editor(material_df, use_container_width=True, hide_index=True)

        merged_df = pd.merge(edited_material_df, edited_unit_price_df, on='材料', how='left')

        merged_df['單價'] = merged_df['單價'].fillna(1)
        merged_df['複價'] = merged_df['數量'] * merged_df['單價']

        total_cost = merged_df['複價'].sum()

    total_cost_len = int(total_cost * cnt)

    st.markdown("---")
    st.markdown("##### 	:small_red_triangle_down:費用計算")
    st.write(f"每座費用:", format(int(total_cost), ','), "元")
    st.write("版橋數量為: " + str(cnt) + " 處")
    st.write("版橋工程費用: **" + str(format(total_cost_len, ',')) + "**元")
    st.write("	:warning: 上述費用 :red[未包含]間接費用")
    # st.session_state.bridge_cost=total_cost_len
    st.session_state['costs']['bridge']['unit_cost'] = total_cost
    st.session_state['costs']['bridge']['quantity'] = cnt
    st.session_state['costs']['bridge']['total_cost'] = total_cost_len
