import streamlit as st
import pandas as pd
from tabs import render_falsework_tab, render_channel_tab, render_bridge_tab, render_road_tab, render_wall_tab


def get_basic_price_data():
    unit_price_data = {
        '材料': ['140kg/cm2混凝土','175kg/cm2混凝土' ,'210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板','AC','碎石級配','CLSM'],
        '單價': [2700, 2750, 2900, 31, 660, 550,360,790,1460],  
        '單位': ['m3','m3', 'm3', 'kg', 'm2','m2','m2','m3','m3']
    }
    return pd.DataFrame(unit_price_data)

def get_falsework_price_data():
    unit_price_data = {
        '材料': ['鋼板樁L=4.5M', '鋼板樁L=6M','鋼板樁L=7M','鋼板樁L=9M','鋼板樁L=13M','鋼軌樁L=4M', '鋼軌樁L=6M','鋼軌樁L=7M','鋼軌樁L=10M','鋼軌樁L=12M'],
        '單價': [2310,2910,3420,3750,4410,1620,1800,1950,2850,3400],  
        '單位': ['每進行m']*10
    }
    return pd.DataFrame(unit_price_data)
def get_cost_data():
    unit_price_data = {
        '項目': ['渠道工程','版橋工程','道路工程','假設工程','擋土工程'],
        '總價': [st.session_state.open_channel_cost,st.session_state.bridge_cost,st.session_state.road_cost,st.session_state.falsework_cost,st.session_state.wall_cost],  
        '單位': ['元']*5
    }

    df=pd.DataFrame(unit_price_data)

    return df

def main():

    # Session_State_Init

    if 'falsework_cost' not in st.session_state:
        st.session_state.falsework_cost = 0
    if 'open_channel_cost' not in st.session_state:
        st.session_state.open_channel_cost = 0
    if 'bridge_cost' not in st.session_state:
        st.session_state.bridge_cost = 0
    if 'road_cost' not in st.session_state:
        st.session_state.road_cost = 0
    if 'wall_cost' not in st.session_state:
        st.session_state.wall_cost = 0
    # Sidebar

    with st.sidebar:
        st.title(":globe_with_meridians: 工程估算系統")
        st.write("這是用於提報計畫時的估算工具")

        st.markdown("---")
        with st.expander(":moneybag: 大宗物資基本單價表"):
            edited_unit_price_df = st.data_editor(get_basic_price_data(), hide_index=True)

        with st.expander(":world_map: 擋土設施基本單價表"):
            edited_falsework_price_df = st.data_editor(get_falsework_price_data(), hide_index=True)
    # Tab

    tab_names = ["渠道工程", "版橋工程","道路工程","假設工程","擋土工程"]

    tabs = st.tabs(tab_names)

    with tabs[0]:
        render_channel_tab(edited_unit_price_df)
    with tabs[1]:
        render_bridge_tab(edited_unit_price_df)
    with tabs[2]:
        render_road_tab(edited_unit_price_df) 
    with tabs[3]:
        render_falsework_tab(edited_falsework_price_df)
    with tabs[4]:
        render_wall_tab(edited_unit_price_df)

    # Sidebar

    with st.sidebar:

        st.markdown("---")
        st.subheader("	:star: 估算結果")
        st.write(":green[直接工程費]")
        # coe=st.number_input("間接費用係數",min_value=0.0,max_value=0.5,step=0.1)

        cost_df=get_cost_data()
        st.dataframe(cost_df, hide_index=True,use_container_width=True) 

        coe=st.number_input("間接費用係數(含雜項)",min_value=0.0,value=0.4,step=0.05,)

        sum_cost=cost_df['總價'].sum()
        formatted_sum_cost = f"{sum_cost:,.0f}"
        st.write(f"直接費用: {formatted_sum_cost} 元")

        formatted_other_cost = f"{sum_cost*coe:,.0f}"
        st.write(f"間接費用: {formatted_other_cost} 元")

        formatted_total_cost = f"{sum_cost*(1+coe):,.0f}"

        st.markdown(f"## :large_orange_diamond: **總費用**為 {formatted_total_cost} 元")

if __name__ == "__main__":
    main()
