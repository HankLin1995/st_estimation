import streamlit as st
from datetime import datetime,date

def session_initialize():

    if 'costs' not in st.session_state:
        st.session_state['costs'] = {
            'open_channel': {'name':'渠道工程','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'bridge': {'name':'版橋工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'wall': {'name':'擋土牆','unit_cost': 0, 'length': 0, 'total_cost': 0},
            'road': {'name':'道路工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0},
            'falsework': {'name':'版樁工程','unit_cost': 0, 'quantity': 0, 'total_cost': 0}
        }

    if 'totalcost' not in st.session_state:
        st.session_state['totalcost'] = 0

    if 'inf' not in st.session_state:
        
        st.session_state['inf'] = {
            'timestamp': datetime.now(),
            'work_place': '雲林縣',
            'work_place2': '斗六市',
            'work_manage':'斗六分處',
            'work_station': '梅林站',
            'work_name': 'OO小給',
            'work_benefit': '20',
            'work_place_water':'處有地',
            'work_place_detail': '已取得並確認妥處',
            'work_water_check':True,
            'work_start_date': date(2024, 1, 1),
            'work_end_date': date(2024, 1, 1),
            'job_length':0,
            'job_cost':0,
            'loss':0

        }

        # 用來暫存點擊的座標
    if 'coords' not in st.session_state:
        st.session_state['coords'] = []

        # 初始化 session_state 中的文件屬性
    if 'uploaded_file1' not in st.session_state:
        st.session_state.uploaded_file1 = None
    if 'uploaded_file2' not in st.session_state:
        st.session_state.uploaded_file2 = None
    if 'uploaded_file3' not in st.session_state:
        st.session_state.uploaded_file3 = None
    if 'uploaded_file4' not in st.session_state:
        st.session_state.uploaded_file4 = None

    if 'tmp_lat' not in st.session_state:
        st.session_state.tmp_lat = 0
    if 'tmp_lon' not in st.session_state:
        st.session_state.tmp_lon = 0

    # 測試使用

    if "test_mode" not in st.session_state:
        st.session_state.test_mode = False
    try:
        if st.query_params["test_mode"] == "1":
            st.session_state.test_mode =True
    except:
        pass
@st.dialog("歡迎使用")
def enter_info(SYSTEM_VERSION):
    st.header(":globe_with_meridians: 工程估算系統 "+SYSTEM_VERSION)
    st.write("這是用於提報計畫時的估算工具")
    st.info("作者:**林宗漢**")
    with st.container(border=True):
        st.write(":clapper: 影片教學(20241120)")
        st.video("./video/demo.mp4")

    st.session_state.logged_in = True
def main():

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    SYSTEM_VERSION="V2.1.0"

    st.set_page_config(
        page_title="工程估算系統"+SYSTEM_VERSION,
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.logo("LOGO.PNG")

    if st.session_state.logged_in == False: enter_info(SYSTEM_VERSION)

    session_initialize()

    tutorial_page = st.Page("view_tutorial.py", title="操作流程", icon=":material/menu_book:")
    logs_page=st.Page("view_logs.py", title="更新日誌", icon=":material/list_alt:")
    info_page = st.Page("view_info.py", title="基本資料", icon=":material/description:")
    map_page = st.Page("view_map.py", title="施作位置", icon=":material/map:")
    item_page = st.Page("view_item.py", title="內容概要", icon=":material/list_alt:")
    projects_page = st.Page("view_projects.py", title="專案管理", icon=":material/folder:")

    pg=st.navigation({

        "基礎教學": [tutorial_page,logs_page],
        "操作介面":[info_page, map_page, item_page],
        "資料管理": [projects_page]
    })

    pg.run()

if __name__ == "__main__":

    main()

    if st.session_state.test_mode ==True:
        st.sidebar.json(st.session_state)
