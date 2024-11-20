import streamlit as st


@st.dialog("輸水損失計算")
def get_irr_loss():

    with st.form(key='effcalc_in'):

        flow=st.number_input("流量")
        leak=st.number_input("滲漏率(%)",help="損失率約(5%~25%)",min_value=5,max_value=25)
        channel_length=st.number_input("渠道總長度")
        improve_length=st.number_input("改善長度")
        actual_effective_irrigation_days=st.number_input("年實際有效灌溉輸水日數",help="通水期間估算")

        submitted = st.form_submit_button("計算")
        try:
            result= int(flow*leak/100*improve_length/channel_length*actual_effective_irrigation_days*86400)
        except:
            pass

        if submitted:
            st.write("流量:", flow)
            st.write("滲漏率:", leak)
            st.write("渠道總長度:", channel_length)
            st.write("改善長度:", improve_length)
            st.write("年實際有效灌溉輸水日數:", actual_effective_irrigation_days)
            st.write("輸水損失",result,"m3/年")
            st.session_state['inf']['loss']=result
            st.rerun()
        
@st.dialog("排水損失計算")
def get_div_loss():

    with st.form(key='effcalc_out'):

        flow=st.number_input("流量")
        leak=st.number_input("破損率(%)",help="破損率約(10%~25%)",min_value=10,max_value=25)
        actual_effective_irrigation_days=st.number_input("年降雨日數(降雨大於5mm)",value=55)

        submitted = st.form_submit_button("計算")

        result= int(flow*leak/100*actual_effective_irrigation_days*86400)

        if submitted:
            st.write("流量:", flow)
            st.write("破損率:", leak)
            st.write("年降雨日數:", actual_effective_irrigation_days)
            st.write("排水損失",result,"m3/年")
            st.session_state['inf']['loss']=result
            st.rerun()

    # 检查并确保日期类型或为空
work_start_date = st.session_state['inf']['work_start_date']
work_end_date = st.session_state['inf']['work_end_date']

if isinstance(work_start_date, (str,)):
    work_start_date = None

if isinstance(work_end_date, (str,)):
    work_end_date = None

if st.sidebar.button("損失效益計算"):
    if st.session_state['inf']['work_type']=="給水":
        get_irr_loss()
    elif st.session_state['inf']['work_type']=="排水":
        get_div_loss()


st.subheader("工程基本資料填報")

col1,col2=st.columns([1,1])

with col1:

    # with st.form("basic_info"):

        col1_left,col1_right=st.columns([1,1])

        with col1_left:
            st.session_state['inf']['work_place'] = st.text_input("縣市別", value=st.session_state['inf']['work_place'])
            # st.session_state['inf']['work_place2'] = st.text_input("鄉鎮市別", value=st.session_state['inf']['work_place2'])
            st.session_state['inf']['work_manage'] = st.selectbox("分處", options=["斗六分處","西螺分處","虎尾分處","北港分處","林內分處"])
            st.session_state['inf']['work_name'] = st.text_input("水路名稱", value=st.session_state['inf']['work_name'])
        with col1_right:
            st.session_state['inf']['work_place2'] = st.text_input("鄉鎮市別", value=st.session_state['inf']['work_place2'])
            # st.session_state['inf']['work_manage'] = st.selectbox("分處", options=["斗六分處","西螺分處","虎尾分處","北港分處","林內分處"])
            st.session_state['inf']['work_station'] = st.text_input("工作站", value=st.session_state['inf']['work_station'])
            st.session_state['inf']['work_type'] = st.selectbox("水路分類", options=["給水","排水"])

        st.session_state['inf']['work_benefit'] = st.text_input("受益面積(ha)", value=st.session_state['inf']['work_benefit'])
        st.session_state['inf']['loss']= st.text_input("損失改善(m3/年)", value=st.session_state['inf']['loss'])

        st.markdown("---")
        st.session_state['inf']['work_place_water'] = st.selectbox("水路用地", options=["處有地","私有地","公有地"])
        st.session_state['inf']['work_place_detail'] = st.selectbox("工程用地", options=["已取得並確認妥處","尚未取得或尚未妥處"])
        # st.session_state['inf']['work_place_detail'] = st.radio("工程用地", options=["已取得並確認妥處","尚未取得或尚未妥處"], 
                                                            # index=0 if st.session_state['inf']['work_place_detail'] != "" else 1)
        # st.session_state['inf']['work_water_check'] = st.selectbox("是否需要配合斷水期施工",options=["是","否"], value=st.session_state['inf']['work_water_check'])
        st.session_state['inf']['work_water_check'] = st.checkbox("需要配合斷水期施工", value=st.session_state['inf']['work_water_check'])
        st.markdown("---")
        st.session_state['inf']['work_start_date'] = st.date_input("最佳施工起始日期", value=work_start_date)
        st.session_state['inf']['work_end_date'] = st.date_input("最佳施工結束日期", value=work_end_date)

        # if st.form_submit_button("儲存"):
        #     st.success("資料已儲存!")

with col2:

    # tab1, tab2, tab3, tab4 = st.tabs(["現地近照", "現地遠照", "設計簡圖", "位置圖"])
    tab1, tab2, tab3 = st.tabs(["現地近照", "現地遠照", "設計簡圖"])

    with tab1:
        if  st.session_state.uploaded_file1 is not None:
            uploaded_file1 = st.file_uploader("現地近照", type=["png", "jpg", "jpeg"], key='upload1')
            if uploaded_file1 is not None:
                st.session_state.uploaded_file1 = uploaded_file1
                st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)
            else:
                st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)
        else:
            uploaded_file1 = st.file_uploader("現地近照", type=["png", "jpg", "jpeg"], key='upload1')
            if uploaded_file1 is not None:
                st.session_state.uploaded_file1 = uploaded_file1
                st.image(st.session_state.uploaded_file1, caption="現地近照", use_column_width=True)

    with tab2:
        if  st.session_state.uploaded_file2 is not None:
            uploaded_file2 = st.file_uploader("現地遠照", type=["png", "jpg", "jpeg"], key='upload2')
            if uploaded_file2 is not None:
                st.session_state.uploaded_file2 = uploaded_file2
                st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)
            else:
                st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)
        else:
            uploaded_file2 = st.file_uploader("現地遠照", type=["png", "jpg", "jpeg"], key='upload2')
            if uploaded_file2 is not None:
                st.session_state.uploaded_file2 = uploaded_file2
                st.image(st.session_state.uploaded_file2, caption="現地遠照", use_column_width=True)

    with tab3:
        if st.session_state.uploaded_file3 is not None:
            uploaded_file3 = st.file_uploader("設計簡圖", type=["png", "jpg", "jpeg"], key='upload3')
            if uploaded_file3 is not None:
                st.session_state.uploaded_file3 = uploaded_file3
                st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)
            else:
                st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)
        else:
            uploaded_file3 = st.file_uploader("設計簡圖", type=["png", "jpg", "jpeg"], key='upload3')
            if uploaded_file3 is not None:
                st.session_state.uploaded_file3 = uploaded_file3
                st.image(st.session_state.uploaded_file3, caption="設計簡圖", use_column_width=True)

    # with tab4:
    #     if  st.session_state.uploaded_file4 is not None:
    #         uploaded_file4 = st.file_uploader("位置圖", type=["png", "jpg", "jpeg"], key='upload4')
    #         if uploaded_file4 is not None:
    #             st.session_state.uploaded_file4 = uploaded_file4
    #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)
    #         else:
    #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)
    #     else:
    #         uploaded_file4 = st.file_uploader("位置圖", type=["png", "jpg", "jpeg"], key='upload4')
    #         if uploaded_file4 is not None:
    #             st.session_state.uploaded_file4 = uploaded_file4
    #             st.image(st.session_state.uploaded_file4, caption="位置圖", use_column_width=True)
