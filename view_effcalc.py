# import streamlit as st

# @st.dialog("輸水損失計算")
# def get_irr_loss():

#     with st.form(key='effcalc_in'):

#         st.markdown("#### 輸水損失計算")
#         st.markdown("---")
#         flow=st.number_input("流量")
#         leak=st.number_input("滲漏率(%)",help="損失率約(5%~25%)",min_value=5,max_value=25)
#         channel_length=st.number_input("渠道總長度")
#         improve_length=st.number_input("改善長度")
#         actual_effective_irrigation_days=st.number_input("年實際有效灌溉輸水日數",help="通水期間估算")

#         submitted = st.form_submit_button("計算")
#         try:
#             result= int(flow*leak/100*improve_length/channel_length*actual_effective_irrigation_days*86400)
#         except:
#             pass

#         if submitted:
#             st.write("流量:", flow)
#             st.write("滲漏率:", leak)
#             st.write("渠道總長度:", channel_length)
#             st.write("改善長度:", improve_length)
#             st.write("年實際有效灌溉輸水日數:", actual_effective_irrigation_days)
#             st.write("輸水損失",result,"m3/年")
#             return result
        
# @st.dialog("排水損失計算")
# def get_div_loss():

#     with st.form(key='effcalc_out'):

#         st.markdown("#### 排水損失計算")
#         st.markdown("---")
#         flow=st.number_input("流量")
#         leak=st.number_input("破損率(%)",help="破損率約(10%~25%)",min_value=10,max_value=25)
#         actual_effective_irrigation_days=st.number_input("年降雨日數(降雨大於5mm)",value=55)

#         submitted = st.form_submit_button("計算")

#         result= int(flow*leak/100*actual_effective_irrigation_days*86400)

#         if submitted:
#             st.write("流量:", flow)
#             st.write("破損率:", leak)
#             st.write("年降雨日數:", actual_effective_irrigation_days)
#             st.write("排水損失",result,"m3/年")
#             return result


#     get_irr_loss()
#     get_div_loss