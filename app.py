import streamlit as st
import pandas as pd
from tabs import render_retaining_wall_tab, render_channel_tab, render_bridge_tab

def main():
    with st.sidebar:

        st.title(":globe_with_meridians: 工程估算系統")
        st.write("這是用於提報計畫時的估算工具")
        st.markdown("---")

        with st.expander(":moneybag: 基本單價表"):

        # st.subheader(":moneybag: 基本單價表")

        # on = st.toggle("是否調整單價?")

        # st.markdown("---")

        # if on:

        # st.write("請根據大宗物資**市場行情**調整")
        # 建立基本單價表
            unit_price_data = {
                '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板','乙種模板','其他'],
                '單價': [2700, 2900, 31, 660,550,1],  # 假設的單價
                '單位': ['m3', 'm3', 'kg', 'm2','m2','式']
            }

            unit_price_df = pd.DataFrame(unit_price_data)
            # edited_unit_price_df = unit_price_df.iloc[:-1, :]
            # edited_unit_price_df = st.data_editor(edited_unit_price_df, hide_index=True)
            edited_unit_price_df = st.data_editor(unit_price_df,hide_index=True)

        # else:
        #     st.write("依據本處發布單價(112.8版本)")

        #     # 建立基本單價表
        #     unit_price_data = {
        #         '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板','乙種模板','其他'],
        #         '單價': [2700, 2900, 31, 660,550,1],  # 假設的單價
        #         '單位': ['m3', 'm3', 'kg', 'm2','m2','式']
        #     }

        #     unit_price_df = pd.DataFrame(unit_price_data)
        #     edited_unit_price_df=unit_price_df
        #     st.dataframe(unit_price_data)

    tab_names = ["擋土工程", "渠道工程", "版橋工程"]

    tabs = st.tabs(tab_names)

    # edited_unit_price_df = st.data_editor(unit_price_df, use_container_width=True, hide_index=True)

    with tabs[0]:
        render_retaining_wall_tab(edited_unit_price_df)
    with tabs[1]:
        render_channel_tab(edited_unit_price_df)
    with tabs[2]:
        render_bridge_tab(edited_unit_price_df)

if __name__ == "__main__":
    main()
