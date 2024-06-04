import streamlit as st
import pandas as pd

def get_materials_typeA(height_cm):

    unit_materails_data = {
        '高度':[60,70,80,90,100,110,120,150,180,200,220,250,280,300],
        '混凝土210': [0.23,0.28,0.34,0.39,0.45,0.51,0.58,0.9,1.19,1.4,1.63,2,2.41,2.7],
        '甲種模板': [0,0,0,0,0,0,0,0,3.74,4.15,4.57,5.19,5.82,6.23],  
        '乙種模板': [1.26,1.47,1.67,1.87,2.08,2.15,2.45,3.12,0,0,0,0,0,0]
    }

    # st.dataframe(unit_materails_data,use_container_width=True)

    if height_cm in unit_materails_data['高度']:
        index = unit_materails_data['高度'].index(height_cm)
        return unit_materails_data['混凝土210'][index], unit_materails_data['甲種模板'][index], unit_materails_data['乙種模板'][index]

def get_materials_typeB(height_cm):

    unit_materails_data = {
        '高度':[200,220,250,300,350,400,450,500,550,600],
        '混凝土140': [0.22,0.25,0.27,0.32,0.37,0.42,0.47,0.52,0.57,0.62],
        '混凝土210': [1.55,1.72,1.97,2.42,2.76,4.16,4.77,5.93,6.04,6.71],
        '鋼筋': [89,95,106,145,169,189,211,283,358,389],
        '甲種模板': [3.2,3.6,4.2,5.2,6,7,8,9,10,11],  
        '乙種模板': [1.3,1.3,1.3,1.3,1.5,1.5,1.5,1.5,1.5,1.5]
    }

    # st.dataframe(unit_materails_data,use_container_width=True)

    if height_cm in unit_materails_data['高度']:
        index = unit_materails_data['高度'].index(height_cm)
        return unit_materails_data['混凝土140'][index], unit_materails_data['混凝土210'][index], unit_materails_data['鋼筋'][index], unit_materails_data['甲種模板'][index], unit_materails_data['乙種模板'][index]

def render_wall_tab(edited_unit_price_df):

    # Initialize variables

    conc140=0.0
    conc175=0.0
    conc210=0.0
    steel=0.0
    frameA=0.0
    frameB=0.0

    # User input

    with st.expander(":pushpin: 擋土牆幾何條件", expanded=True):

        op=st.radio("請選擇擋土牆型式", ("重力式擋土牆","懸臂式擋土牆"))

        # if op=="L型擋土牆(自行設定單元材料)":
        #     IsExpander=True
        if op=="重力式擋土牆":
            height_cm=st.selectbox("請輸入擋土牆高度(cm)",options=[60,70,80,90,100,110,120,150,180,200,220,250,280,300])
            conc175,frameA,frameB=get_materials_typeA(height_cm)
            IsExpander=False
        elif op=="懸臂式擋土牆":
            height_cm=st.selectbox("請輸入擋土牆高度(cm)",options=[200,220,250,300,350,400,450,500,550,600])
            conc140,conc210,steel,frameA,frameB=get_materials_typeB(height_cm)
            IsExpander=False

        cnt=st.number_input("施作長度(m)", min_value=0.0, value=0.0, step=0.1)

    material_data = {
        '材料': ['140kg/cm2混凝土','175kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板', '乙種模板', '其他'],
        '數量': [conc140,conc175, conc210, steel, frameA, frameB, 0],
        '單位': ['m3', 'm3','m3', 'kg', 'm2', 'm2', '元']
    }
    material_df = pd.DataFrame(material_data)

    with st.expander(":signal_strength: 材料計算表(每m)", expanded=IsExpander):

        edited_material_df = st.data_editor(material_df, use_container_width=True, hide_index=True)

        merged_df = pd.merge(edited_material_df, edited_unit_price_df, on='材料', how='left')

        merged_df['單價'] = merged_df['單價'].fillna(1)
        merged_df['複價'] = merged_df['數量'] * merged_df['單價']

        total_cost = merged_df['複價'].sum()

    total_cost_len = int(total_cost * cnt)
    st.markdown("---")
    st.markdown("### 	:small_red_triangle_down:費用計算")
    st.write(f"每進行米費用:", format(int(total_cost), ','), "元")
    st.write("擋土牆長度為: " + str(cnt) + " M")
    st.write("擋土工程費用: **" + str(format(total_cost_len, ',')) + "**元")
    st.write("	:warning: 上述費用 :red[未包含]間接費用")
    # st.session_state.wall_cost=total_cost_len
    st.session_state['costs']['wall']['unit_cost'] = int(total_cost)
    st.session_state['costs']['wall']['length'] = cnt
    st.session_state['costs']['wall']['total_cost'] = total_cost_len