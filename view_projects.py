import streamlit as st
import pandas as pd
from datetime import datetime, date
from api_client import APIClient

# 初始化 API Client
api_client = APIClient()

def format_datetime(dt):
    """格式化日期時間"""
    if dt:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    return "未設定"


def format_currency(amount):
    """格式化金額"""
    if amount:
        return f"NT$ {amount:,.0f}"
    return "NT$ 0"


@st.dialog("🗑️ 刪除水路")
def delete_project_form(project_id):
    """刪除專案表單"""
    project = api_client.get_project(project_id)
    if not project:
        st.error("找不到指定的專案")
        return
    
    if st.button("刪除"):
        try:
            api_client.delete_project(project_id)
            st.success("專案刪除成功！")
            st.rerun()
        except Exception as e:
            st.error(f"刪除失敗：{e}")

@st.dialog("✏️ 編輯水路",width="large")
def edit_project_form(project_id):
    """編輯專案表單"""
    project = api_client.get_project(project_id)
    if not project:
        st.error("找不到指定的專案")
        return
    
    with st.form(f"edit_project_{project_id}"):
        st.markdown("#### 基本資訊")
        
        col1, col2 = st.columns(2)
        
        with col1:
            work_name = st.text_input("工程名稱 *", value=project.get("work_name", ""))
            work_place = st.text_input("縣市", value=project.get("work_place", ""))
            work_place2 = st.text_input("鄉鎮市", value=project.get("work_place2", ""))
            work_manage = st.text_input("分處", value=project.get("work_manage", ""))
            work_station = st.text_input("工作站", value=project.get("work_station", ""))
        
        with col2:
            waterway_type = st.selectbox("水路分類", options=["給水","排水"])
            work_benefit = st.text_input("受益面積 (ha)", value=str(project.get("work_benefit", "")))
            job_length = st.number_input("水路長度 (m)", min_value=0.0, value=float(project.get("job_length", 0)), step=10.0)
            job_cost = st.number_input("工程經費 (元)", min_value=0.0, value=float(project.get("job_cost", 0)), step=10000.0)
            work_water_check = st.checkbox("需配合斷水期施工", value=project.get("work_water_check", False))
        
        st.markdown("#### 施工期程")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date_value = date.today()
            if project.get("work_start_date"):
                try:
                    dt = datetime.fromisoformat(project["work_start_date"].replace('Z', '+00:00'))
                    start_date_value = dt.date()
                except:
                    pass
            work_start_date = st.date_input("施工起始日", value=start_date_value)
        
        with col2:
            end_date_value = date.today()
            if project.get("work_end_date"):
                try:
                    dt = datetime.fromisoformat(project["work_end_date"].replace('Z', '+00:00'))
                    end_date_value = dt.date()
                except:
                    pass
            work_end_date = st.date_input("施工結束日", value=end_date_value)
        
        st.markdown("#### 其他資訊")
        col1, col2 = st.columns(2)
        
        with col1:
            work_place_water = st.text_input("用地狀況", value=project.get("work_place_water", ""))
        
        with col2:
            work_place_detail = st.selectbox(
                "用地取得",
                ["已取得並確認妥處", "尚未取得"],
                index=0 if project.get("work_place_detail") == "已取得並確認妥處" else 1
            )
        
        benefit_description = st.text_area(
            "效益說明",
            value=project.get("benefit_description", ""),
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("儲存變更", width="stretch")
        with col2:
            if st.form_submit_button("取消", type="secondary", width="stretch"):
                return
        
        if submitted:
            if not work_name:
                st.error("請輸入工程名稱")
                return
            
            update_data = {
                "work_name": work_name,
                "work_place": work_place,
                "work_place2": work_place2,
                "work_manage": work_manage,
                "work_station": work_station,
                "waterway_type": waterway_type,
                "work_benefit": work_benefit,
                "benefit_description": benefit_description,
                "work_place_water": work_place_water,
                "work_place_detail": work_place_detail,
                "work_water_check": work_water_check,
                "work_start_date": datetime.combine(work_start_date, datetime.min.time()).isoformat(),
                "work_end_date": datetime.combine(work_end_date, datetime.min.time()).isoformat(),
                "job_length": job_length,
                "job_cost": job_cost
            }
            
            try:
                result = api_client.update_project(project_id, update_data)
                st.success("專案更新成功！")
                st.rerun()
            except Exception as e:
                st.error(f"更新失敗：{e}")


@st.dialog("📄 水路詳情",width="large")
def show_project_detail(project_id):
    """顯示專案詳情"""
    project = api_client.get_project(project_id)
    
    if not project:
        st.error(f"找不到水路 ID: {project_id}")
        return
    
    # 基本資訊
    st.markdown("#### 基本資訊")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("水路 ID", project["id"])
        st.write(f"**工程名稱**: {project['work_name']}")
        st.write(f"**縣市**: {project.get('work_place', '')}")
        st.write(f"**鄉鎮**: {project.get('work_place2', '')}")
    
    with col2:
        st.write(f"**分處**: {project.get('work_manage', '')}")
        st.write(f"**工作站**: {project.get('work_station', '')}")
        st.write(f"**水路分類**: {project.get('waterway_type', '')}")
        st.write(f"**受益面積**: {project.get('work_benefit', '')} ha")
    
    with col3:
        st.write(f"**水路長度**: {project.get('job_length', 0)} m")
        st.write(f"**工程經費**: {format_currency(project.get('job_cost', 0))}")
        st.write(f"**需斷水施工**: {'是' if project.get('work_water_check') else '否'}")
    
    # 施工期程
    st.markdown("#### 施工期程")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**施工起始日**: {format_datetime(project.get('work_start_date'))}")
    
    with col2:
        st.write(f"**施工結束日**: {format_datetime(project.get('work_end_date'))}")
    
    # 效益說明
    if project.get('benefit_description'):
        st.markdown("#### 效益說明")
        st.info(project['benefit_description'])
    
    # 座標資訊
    st.markdown("#### 📍 座標資訊")
    coords = api_client.get_project_coordinates(project_id)
    
    if coords:
        coord_data = []
        for coord in coords:
            coord_data.append({
                "順序": coord.get("order", ""),
                "描述": coord.get("description", ""),
                "TWD97 X": coord.get("twd97_x", ""),
                "TWD97 Y": coord.get("twd97_y", "")
            })
        df_coords = pd.DataFrame(coord_data)
        st.dataframe(df_coords, width="stretch", hide_index=True)
    else:
        st.info("尚無座標資料")
    
    # 圖片資訊
    st.markdown("#### 🖼️ 圖片資訊")
    images = api_client.get_project_images(project_id)
    
    if images:
        image_types = {"設計圖": "設計圖", "近照": "近照", "遠照": "遠照"}
        cols = st.columns(3)
        for idx, (type_name, type_code) in enumerate(image_types.items()):
            with cols[idx]:
                type_images = [img for img in images if img.get("image_type") == type_code]
                if type_images:
                    st.markdown(f"**{type_name}** ({len(type_images)})")
                    for img in type_images:
                        # 獲取並顯示圖片
                        image_content = api_client.get_image_file(img['id'])
                        if image_content:
                            st.image(image_content, caption=img.get('file_name', ''), use_container_width=True)
                        else:
                            st.warning(f"⚠️ 無法載入: {img.get('file_name', '')}")
                else:
                    st.info(f"無{type_name}")
    else:
        st.info("尚無圖片資料")


def display_projects(df):
    """顯示專案列表"""
    df_display = df[[
        'id', 'work_name', 'work_place', 'work_place2', 
        'work_manage', 'work_station', 'waterway_type', 
        'work_benefit', 'job_cost', 'created_at'
    ]].copy()
    
    # 格式化顯示
    df_display['job_cost'] = df_display['job_cost'].apply(lambda x: f"NT$ {x:,.0f}" if x else "NT$ 0")
    df_display['created_at'] = df_display['created_at'].apply(format_datetime)
    
    event = st.dataframe(
        df_display,
        column_config={
            'id': 'ID',
            'work_name': '工程名稱',
            'work_place': '縣市',
            'work_place2': '鄉鎮',
            'work_manage': '分處',
            'work_station': '工作站',
            'waterway_type': None,
            'work_benefit': '受益面積',
            'job_cost': '工程經費',
            'created_at': '建立時間'
        },
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        width="stretch"
    )
    
    select_projects = event.selection.rows
    filtered_df = df.iloc[select_projects]
    
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 查看詳情", width="stretch"):
                show_project_detail(filtered_df.iloc[0]["id"])
        
        with col2:
            if st.button("✏️ 編輯水路", width="stretch"):
                edit_project_form(filtered_df.iloc[0]["id"])
        
        with col3:
            if st.button("🗑️ 刪除水路", width="stretch"):
                delete_project_form(filtered_df.iloc[0]["id"])

##### MAIN UI #####

# 檢查後端連接
if not api_client.health_check():
    st.error("❌ 無法連接到後端伺服器")
    st.info("請確認後端服務是否正在運行")
    st.stop()

# 取得專案列表
projects = api_client.get_projects()

if projects is None:
    st.error("❌ 無法取得專案列表")
    st.stop()

df_projects = pd.DataFrame(projects)

# 標題
st.markdown("### 📁 水路管理")

if df_projects.empty:
    st.info("目前沒有水路資料")
else:
    display_projects(df_projects)
