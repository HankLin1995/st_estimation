import streamlit as st
import pandas as pd
from tabs import render_retaining_wall_tab, render_channel_tab, render_bridge_tab, render_road_tab

def main():
    with st.sidebar:
        st.title(":globe_with_meridians: 工程估算系統")
        st.write("這是用於提報計畫時的估算工具")
        st.markdown("---")

        with st.expander(":moneybag: 基本單價表"):
            unit_price_data = {
                '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板',  
                        '鋼板樁4.5m', '鋼板樁6m', '鋼板樁7m', '鋼板樁9m', '鋼板樁13m', 
                        '鋼軌樁4m', '鋼軌樁6m', '鋼軌樁7m', '鋼軌樁10m', '鋼軌樁12m'],
                '單價': [2700, 2900, 31, 660, 550,  
                         2310, 2910, 3420, 3750, 4410, 
                         1620, 1800, 1950, 2850, 3400],  # 使用提供的單價
                '單位': ['m3', 'm3', 'kg', 'm2', 'm2',  
                         'm', 'm', 'm', 'm', 'm', 
                         'm', 'm', 'm', 'm', 'm']
            }
            unit_price_df = pd.DataFrame(unit_price_data)
            edited_unit_price_df = st.data_editor(unit_price_df, hide_index=True)

    if 'retaining_wall_cost' not in st.session_state:
        st.session_state.retaining_wall_cost = []
    if 'open_channel_cost' not in st.session_state:
        st.session_state.open_channel_cost = []
    if 'bridge_cost' not in st.session_state:
        st.session_state.bridge_cost = []

    tab_names = ["擋土工程", "渠道工程", "版橋工程","道路工程","安全設施"]

    tabs = st.tabs(tab_names)

    with tabs[0]:
        render_retaining_wall_tab(edited_unit_price_df)
    with tabs[1]:
        render_channel_tab(edited_unit_price_df)
    with tabs[2]:
        render_bridge_tab(edited_unit_price_df)
    with tabs[3]:
        render_road_tab(edited_unit_price_df)  

if __name__ == "__main__":
    main()
