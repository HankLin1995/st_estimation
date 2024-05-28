import streamlit as st
import pandas as pd
import numpy as np

def calculate_materials(width, height):
    # 假設的計算公式，具體公式需根據實際情況調整
    wall_thickness=get_wall_thickness(height)

    volume_140_concrete = 0.1*(wall_thickness*2+width+0.1*2)#*length  
    volume_210_concrete = wall_thickness*(wall_thickness*2+width+0.05*2)#*length  
    weight_steel = interpolate_rebar_amount(height)#*length  # 假設需要鋼筋的重量
    area_formwork_A=0
    area_formwork_B=0
    if height>=1.5:
        area_formwork_A = (0.1+wall_thickness)*2+height*4  # 假設需要模板的面積
    else:
        area_formwork_B=(0.1+wall_thickness)*2+height*4  # 假設需要模板的面積

    return volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B

def calculate_materials_bridge(width, length):
    # 假設的計算公式，具體公式需根據實際情況調整

    bridge_thickness=get_wall_thickness_bridge(width)

    volume_140_concrete = 0 #*length  
    volume_210_concrete = bridge_thickness*(width*length)  
    weight_steel = interpolate_rebar_amount_bridge(width)*length  # 假設需要鋼筋的重量
    area_formwork_A=0
    area_formwork_B=0
    if width>=1.5:
        area_formwork_A = 2*(width+length)*bridge_thickness  # 假設需要模板的面積
    else:
        area_formwork_B=2*(width+length)*bridge_thickness  # 假設需要模板的面積

    return volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A, area_formwork_B

def get_wall_thickness(height):
    """
    根據牆身高度返回牆厚。

    :param height: 牆身高度 (m)
    :return: 牆厚 (m)
    """
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
        return 0.4  # 如果高度不在範圍內，返回 None 或其他適當值

def get_wall_thickness_bridge(width):
    """
    根據牆身高度返回牆厚。

    :param width: 牆身高度 (m)
    :return: 牆厚 (m)
    """
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
        return 0.5  # 如果高度不在範圍內，返回 None 或其他適當值

def interpolate_rebar_amount(height):
    """
    根據牆身高度返回鋼筋量的內插值。

    :param height: 牆身高度 (m)
    :return: 鋼筋量
    """
    heights = [0, 1.0, 1.5, 2.0, 2.5, 3.0]
    rebar_amounts = [24,24, 33, 52, 57, 78]  # 為了避免3.0m以上無法內插，將3.0m的鋼筋量設置為78

    if height <= 0:
        return rebar_amounts[0]
    elif height >= 3.0:
        return rebar_amounts[-1]
    else:
        return np.interp(height, heights, rebar_amounts)
def interpolate_rebar_amount_bridge(width):
    """
    根據牆身高度返回鋼筋量的內插值。

    :param height: 牆身高度 (m)
    :return: 鋼筋量
    """
    widths = [0, 1.0, 2.0, 3.0, 4.0, 5.0]
    rebar_amounts = [16,16, 21, 27, 41, 51]  

    if width <= 0:
        return rebar_amounts[0]
    elif width >= 5.0:
        return rebar_amounts[-1]
    else:
        return np.interp(width, widths, rebar_amounts)
    
def main():

    with st.sidebar:

        st.title(":globe_with_meridians: 工程估算系統")
        st.write("這是用於提報計畫時的估算工具")
        st.markdown("---")

        st.subheader(":moneybag: 基本單價表")

        on = st.toggle("是否調整單價?")

        st.markdown("---")

        if on:

            st.write("請根據大宗物資**市場行情**調整")
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

        else:
            st.write("依據本處發布單價(112.8版本)")

            # 建立基本單價表
            unit_price_data = {
                '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板','乙種模板','其他'],
                '單價': [2700, 2900, 31, 660,550,1],  # 假設的單價
                '單位': ['m3', 'm3', 'kg', 'm2','m2','式']
            }

            unit_price_df = pd.DataFrame(unit_price_data)
            edited_unit_price_df=unit_price_df
            st.dataframe(unit_price_data)

    tab1, tab2, tab3,tab4,tab5,tab6 = st.tabs(["擋土工程", "渠道工程", "版橋工程","道路工程","安全設施","假設工程"])

    with tab1:
        st.write(":blue[:point_down: 請根據實際需求填寫長度]")

        # 建立基本單價表
        foundation_data = {
            '材料': ['鋼板樁L=4.5M', '鋼板樁L=6M','鋼板樁L=7M','鋼板樁L=9M','鋼板樁L=13M'],
            '單價':[2310,2910,3420,3750,4410],
            '長度': [0, 0,0,0,0],  
            '單位': ['每進行米', '每進行米','每進行米','每進行米','每進行米']
        }

        foundation_df = pd.DataFrame(foundation_data)
        edited_foundation_df = st.data_editor(foundation_df,hide_index=True)

        # 建立基本單價表
        foundation2_data = {
            '材料': ['鋼軌樁L=4M', '鋼軌樁L=6M','鋼軌樁L=7M','鋼軌樁L=10M','鋼軌樁L=12M'],
            '單價':[1620,1800,1950,2850,3400],
            '長度': [0, 0,0,0,0],  
            '單位': ['每進行米', '每進行米','每進行米','每進行米','每進行米']
        }

        foundation2_df = pd.DataFrame(foundation2_data)
        edited_foundation2_df = st.data_editor(foundation2_df,hide_index=True)

        # 重新計算複價
        edited_foundation2_df['複價'] = edited_foundation2_df['單價'] * edited_foundation2_df['長度']
        edited_foundation_df['複價'] = edited_foundation_df['單價'] * edited_foundation_df['長度']

        # 重新計算總複價
        total_cost_foundation = edited_foundation_df['複價'].sum()
        total_cost_foundation2 = edited_foundation2_df['複價'].sum()

        # 計算總費用
        total_cost = total_cost_foundation + total_cost_foundation2

        # 顯示結果
        st.markdown("---")
        st.write("擋土工程費用: **"+str(format(total_cost, ','))+"**元")
        st.write("	:warning: 上述費用 :red[未包含]間接費用")

    with tab2:

        with st.expander(":pushpin: 明渠幾何條件",expanded=True):

            col1, col2 = st.columns([1,1])

            with col1:
                # st.write("**相關尺寸:**")
                width = st.number_input("寬度b (m)", min_value=0.0, value=1.0, step=0.1)
                height = st.number_input("高度H (m)", min_value=0.0,max_value=3.0, value=1.0, step=0.1)
                length = st.number_input("長度L (m)", min_value=0.0, value=0.0, step=0.1)

            with col2:
                    
                # st.image('photos/images.jpg', caption='U型溝照片範例',width=200)
                st.image('photos/images.jpg', caption='渠道範例')

            # 根據尺寸計算所需的材料數量
            volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A,area_formwork_B = calculate_materials(width, height)

            # 建立材料計算表
            material_data = {
                '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板','乙種模板','其他'],
                '數量': [volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A,area_formwork_B,0],
                '單位': ['m3', 'm3', 'kg', 'm2','m2','元']
            }
            material_df = pd.DataFrame(material_data)

        with st.expander(":signal_strength: 材料計算表(每進行米)"):
            # st.write("請編輯下表中的數據：")
            edited_material_df = st.data_editor(material_df, use_container_width=True,hide_index=True)

            merged_df = pd.merge(edited_material_df, edited_unit_price_df, on='材料')
            merged_df['複價'] = merged_df['數量'] * merged_df['單價']

            total_cost = merged_df['複價'].sum()

        total_cost_len=int(total_cost*length)

        st.markdown("---")
        st.write(f"每進行米費用:" ,format(int(total_cost),','),"元")
        st.write("渠道長度為: "+str(length)+" 米")
        st.write("渠道工程費用: **"+str(format(total_cost_len, ','))+"**元")
        st.write("	:warning: 上述費用 :red[未包含]間接費用")

    with tab3:

        with st.expander(":pushpin: 版橋幾何條件",expanded=True):

            col1, col2 = st.columns([1,1])

            with col1:
                # st.write("**相關尺寸:**")
                width = st.number_input("寬度W (m)", min_value=0.0,max_value=5.0,value=1.0, step=0.1)
                length = st.number_input("長度L (m)", min_value=0.0,max_value=6.0, value=1.0, step=0.1)
                # thickness = st.number_input("厚度T (m)", min_value=0.0, value=0.0, step=0.1)
                thickness=get_wall_thickness_bridge(width)
                
                cnt = st.number_input("數量 (處)", min_value=0.0, value=0.0, step=0.1)

                st.write("*推估厚度T: ",thickness," m")

            with col2:
                    
                # st.image('photos/images.jpg', caption='U型溝照片範例',width=200)
                st.image('photos/images_bridge.jpg', caption='版橋範例')

            # 根據尺寸計算所需的材料數量
            volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A,area_formwork_B = calculate_materials_bridge(width, length)

            # 建立材料計算表
            material_data = {
                '材料': ['140kg/cm2混凝土', '210kg/cm2混凝土', '鋼筋', '甲種模板','乙種模板','其他'],
                '數量': [volume_140_concrete, volume_210_concrete, weight_steel, area_formwork_A,area_formwork_B,0],
                '單位': ['m3', 'm3', 'kg', 'm2','m2','元']
            }
            material_df = pd.DataFrame(material_data)

        with st.expander(":signal_strength: 材料計算表(每處)"):
            # st.write("請編輯下表中的數據：")
            edited_material_df = st.data_editor(material_df, use_container_width=True,hide_index=True)

            merged_df = pd.merge(edited_material_df, edited_unit_price_df, on='材料')

            merged_df['複價'] = merged_df['數量'] * merged_df['單價']

            total_cost = merged_df['複價'].sum()

        total_cost_len=int(total_cost*cnt)

        st.markdown("---")
        st.write(f"每處費用:" ,format(int(total_cost),','),"元")
        st.write("版橋數量為: "+str(cnt)+" 處")
        st.write("版橋工程費用: **"+str(format(total_cost_len, ','))+"**元")
        st.write("	:warning: 上述費用 :red[未包含]間接費用")



if __name__ == "__main__":
    main()
