import streamlit as st
import pandas as pd
from tabs import render_falsework_tab, render_channel_tab, render_bridge_tab, render_road_tab, render_wall_tab
import openpyxl
import os

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
    cost_data = []
    for key, item in st.session_state['costs'].items():
        # if 'length' in item:
        #     description = f"{item['unit_cost']}元/每進行m * {item['length']}m"
        # elif 'quantity' in item:
        #     description = f"{item['unit_cost']}元/每座 * {item['quantity']}座"
        cost_data.append({
            '項目': item['name'],
            # '單位成本': item['unit_cost'],
            '總價': item['total_cost'],
            '單位': '元'
            # '描述': description,
        })

    # 將資料轉換為 DataFrame
    cost_df = pd.DataFrame(cost_data)

    return cost_df

# 定義函數輸出文字串
def generate_cost_report(costs, indirect_coefficient=0.4):
    report = []
    total_direct_cost = 0
    index = 1

    for key, item in costs.items():
        total_cost = item['total_cost']
        if total_cost == 0:
            continue
        
        if key in ['road', 'falsework']:
            description = f"{total_cost:,.0f}元"
        else:
            if 'length' in item:
                description = f"{item['unit_cost']:,.0f}元/每進行m * {item['length']:,.0f}m"
            elif 'quantity' in item:
                description = f"{item['unit_cost']:,.0f}元/每座 * {item['quantity']:,.0f}座"
            description += f" = {total_cost:,.0f}元"
        
        report.append(f"{index}. {item['name']}: {description}")
        total_direct_cost += total_cost
        index += 1

    indirect_cost = round(total_direct_cost * (1+indirect_coefficient),-3)-total_direct_cost
    total_cost = total_direct_cost + indirect_cost

    report.append(f"\n直接工程費 = {total_direct_cost:,.0f}元")
    report.append(f"間接工程費(含雜項) = 直接工程費 * {indirect_coefficient} = {indirect_cost:,.0f}元")
    report.append(f"\n總工程費 = {total_cost:,.0f}元")

    return "\n".join(report)
def main():

    # 初始化 session_state 中的資料
    if 'costs' not in st.session_state:

        st.session_state['costs'] = {
            'open_channel': {'name':'渠道工程','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'bridge': {'name':'版橋工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'wall': {'name':'擋土牆','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'road': {'name':'道路工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'falsework': {'name':'版樁工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0}
        }

    # Sidebar

    with st.sidebar:
        st.title(":globe_with_meridians: 工程估算系統")
        st.write("這是用於提報計畫時的估算工具")
        st.info("作者:**林宗漢**")
        st.markdown("---")
        with st.expander(":moneybag: 大宗物資基本單價表"):
            edited_unit_price_df = st.data_editor(get_basic_price_data(), hide_index=True)

        with st.expander(":world_map: 擋土設施基本單價表"):
            edited_falsework_price_df = st.data_editor(get_falsework_price_data(), hide_index=True)
    # Tab

    tab_names = ["渠道工程", "版橋工程","道路工程","版樁工程","擋土牆"]

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

        # 顯示估算結果
        st.subheader(":star: 估算結果")
        st.write(":green[直接工程費]")

        cost_df=get_cost_data()
        st.dataframe(cost_df, hide_index=True, use_container_width=True)

        # 輸入間接費用係數
        coe = st.number_input("間接費用係數(含雜項)", min_value=0.0, value=0.4, step=0.05)

        # 計算費用
        sum_cost = cost_df['總價'].sum()
        other_cost=round(sum_cost * (1+coe),-3)-sum_cost
        total_cost=sum_cost+other_cost

        formatted_sum_cost = f"{sum_cost:,.0f}"
        formatted_other_cost = f"{other_cost:,.0f}"
        formatted_total_cost = f"{total_cost:,.0f}"

        st.write(f"直接費用: {formatted_sum_cost} 元")
        st.write(f"間接費用: {formatted_other_cost} 元")
        st.markdown(f"## :large_orange_diamond: **總費用**為 {formatted_total_cost} 元")

        st.markdown("---")

        if st.button("工程概要表", type="primary"):
        # 生成報告
            report = generate_cost_report(st.session_state['costs'],coe)
            # st.text(report)

             #----Excel報表內容填寫----
            workbook = openpyxl.load_workbook('./template/PLAN.xlsx')

            sheet = workbook["概要表"]

            # 将数字写入指定单元格，例如将数字 123 写入第一行第一列的单元格
            sheet.cell(row=3, column=8).value =report

            output_file = 'example.xlsx'
            workbook.save(output_file)

            with open(output_file, 'rb') as f:
                bytes_data = f.read()
            st.sidebar.download_button(label='計算成果下載', data=bytes_data, file_name=output_file,type='primary')

            os.remove(output_file)
if __name__ == "__main__":
    main()
