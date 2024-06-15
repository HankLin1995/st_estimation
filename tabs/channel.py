import streamlit as st
import pandas as pd
import numpy as np

def calculate_materials(width, height):

    rebar_protection=0.05

    wall_thickness = get_wall_thickness(height)

    volume_140_concrete = 0.1 * (wall_thickness * 2 + width + 0.1 * 2)
    volume_210_concrete = wall_thickness * (wall_thickness * 2 + width + 0.05 * 2)+wall_thickness*height*2
    # weight_steel = interpolate_rebar_amount(height)
    area_formwork_A = 0
    area_formwork_B = 0
    if height >= 1.5:
        area_formwork_A = (0.1 + wall_thickness) * 2 + height * 4
    else:
        area_formwork_B = (0.1 + wall_thickness) * 2 + height * 4

    L1=width+2*height+4*wall_thickness-6*rebar_protection
    L1_temp=int(L1/0.2)+2

    L2=L1#width+2*height+2*rebar_protection
    L2_temp=int(L2/0.2)+2

    weight_steel=calc_rebar_weight(L1,L1_temp,L2,L2_temp,height)

    return volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B

def calc_rebar_weight(L1,L1_temp,L2,L2_temp,height):
    
    if height < 1.0:
        L1_num=4
        L1_temp_num=3
        L2_num=0
        L2_temp_num=0
    elif 1.0 <= height < 1.5:
        L1_num=5
        L1_temp_num=3
        L2_num=0
        L2_temp_num=0
    elif 1.5 <=height < 2.0:
        L1_num=6
        L1_temp_num=4
        L2_num=0
        L2_temp_num=0
    elif 2.0 <=height < 2.5:
        L1_num=5
        L1_temp_num=3
        L2_num=4
        L2_temp_num=3
    elif 2.5 <= height <= 3.0:
        L1_num=6
        L1_temp_num=3
        L2_num=5
        L2_temp_num=3

    rebar_unit_weight,rebar_loss=get_rebar_weight_loss(L1_num)
    L1_weight=L1*rebar_unit_weight*rebar_loss*(1/0.2)
    rebar_unit_weight,rebar_loss=get_rebar_weight_loss(L1_temp_num)
    L1_temp_weight=L1_temp*rebar_unit_weight*rebar_loss
    rebar_unit_weight,rebar_loss=get_rebar_weight_loss(L2_num)
    L2_weight=L2*rebar_unit_weight*rebar_loss*(1/0.2)
    rebar_unit_weight,rebar_loss=get_rebar_weight_loss(L2_temp_num)
    L2_temp_weight=L2_temp*rebar_unit_weight*rebar_loss

    rebar_total_weight=L1_weight+L1_temp_weight+L2_weight+L2_temp_weight

    return rebar_total_weight

def get_rebar_weight_loss(rebar_num):
    if rebar_num==3:
        return 0.559,1.065
    elif rebar_num==4:
        return 0.994,1.065
    elif rebar_num==5:
        return 1.56,1.065
    elif rebar_num==6:
        return 2.24,1.1
    elif rebar_num==0:
        return 0,0
        

def get_wall_thickness(height):
    if height < 1.0:
        return 0.2
    elif 1.0 <= height < 1.5:
        return 0.2
    elif 1.5 <= height < 2.0:
        return 0.2
    elif 2.0 <= height < 2.5:
        return 0.25
    elif 2.5 <= height <= 3.0:
        return 0.3
    else:
        return 0.4

# def interpolate_rebar_amount(height):
#     heights = [0, 1.0, 1.5, 2.0, 2.5, 3.0]
#     rebar_amounts = [29, 29, 57, 115, 165, 263]

#     if height <= 0:
#         return rebar_amounts[0]
#     elif height >= 3.0:
#         return rebar_amounts[-1]
#     else:
#         return np.interp(height, heights, rebar_amounts)
    
def input_and_update_state(label, session_key, default_value, min_value=None, max_value=None, step=None):
    if session_key not in st.session_state:
        st.session_state[session_key] = default_value  # 預設值

    value = st.number_input(label, min_value=min_value, max_value=max_value, value=st.session_state.get(session_key), step=step)
    st.session_state[session_key] = value  # 更新值
    return value
def render_channel_tab(edited_unit_price_df):
    with st.expander(":pushpin: 明渠幾何條件", expanded=True):
        col1, col2 = st.columns([1, 1])

        with col1:
            # 寬度b (m)
            width = input_and_update_state("寬度b (m)", "channel_width", 1.0, min_value=0.0, step=0.1)

            # 高度H (m)
            height = input_and_update_state("高度H (m)", "channel_height", 1.0, min_value=0.0, max_value=3.0, step=0.1)

            # 長度L (m)
            length = input_and_update_state("長度L (m)", "channel_length", 0.0, min_value=0.0, step=0.1)

            # 推估厚度T
            thickness = get_wall_thickness(height)
            st.write("*推估厚度T: ", thickness, " m")

        with col2:
            st.image('photos/images.jpg', caption='渠道範例')

        volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B = calculate_materials(width, height)

        material_data = {
            '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板', '其他'],
            '數量': [volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B, 0],
            '單位': ['m3', 'm3', 'kg', 'm2', 'm2', '元']
        }
        material_df = pd.DataFrame(material_data)

    with st.expander(":signal_strength: 材料計算表(每進行米)"):
        edited_material_df = st.data_editor(material_df, use_container_width=True, hide_index=True)

        merged_df = pd.merge(edited_material_df, edited_unit_price_df, on='材料', how='left')

        merged_df['單價'] = merged_df['單價'].fillna(1)
        merged_df['複價'] = merged_df['數量'] * merged_df['單價']

        total_cost = merged_df['複價'].sum()

    total_cost_len = int(total_cost * length)

    st.markdown("---")
    st.markdown("##### 	:small_red_triangle_down:費用計算")
    st.write(f"每進行米費用:", format(int(total_cost), ','), "元")
    st.write("渠道長度為: " + str(length) + " 米")
    st.write("渠道工程費用: **" + str(format(total_cost_len, ',')) + "**元")
    st.write("	:warning: 上述費用 :red[未包含]間接費用")
    # st.session_state.open_channel_cost=total_cost_len
    st.session_state['costs']['open_channel']['unit_cost'] = total_cost
    st.session_state['costs']['open_channel']['length'] = length
    st.session_state['costs']['open_channel']['total_cost'] = total_cost_len
