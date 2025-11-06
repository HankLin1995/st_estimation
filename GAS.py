"""
資料獲取模組
從後端 API 獲取專案資料用於會勘管理
"""
import streamlit as st
import pandas as pd
from api_client import APIClient


@st.cache_data
def getOriginData():
    """從後端 API 獲取專案資料"""
    api_client = APIClient()
    
    # 獲取所有專案
    projects = api_client.get_projects(limit=1000)
    
    if not projects:
        st.warning("無法獲取專案資料")
        return pd.DataFrame()
    
    # 轉換為會勘管理所需的格式
    filtered_records = []
    
    for project in projects:
        # 獲取專案座標（取第三個座標點，對應會勘點）
        coords = api_client.get_project_coordinates(project['id'])
        
        # 預設座標（如果沒有座標資料）
        lat = 23.7089
        lon = 120.5406
        
        # 如果有座標資料，使用會勘點（第三個點）或第一個點
        if coords and len(coords) > 0:
            # 優先使用描述為「會勘點」的座標
            meeting_coord = next((c for c in coords if c.get('description') == '會勘點'), None)
            if meeting_coord:
                lat = meeting_coord.get('twd97_y', lat)
                lon = meeting_coord.get('twd97_x', lon)
            elif len(coords) >= 3:
                # 使用第三個座標點
                lat = coords[2].get('twd97_y', lat)
                lon = coords[2].get('twd97_x', lon)
            else:
                # 使用第一個座標點
                lat = coords[0].get('twd97_y', lat)
                lon = coords[0].get('twd97_x', lon)
        
        filtered_record = {
            'meeting': False,  # 預設不選取
            'id': project['id'],
            'inf.work_place2': project.get('work_place2', ''),
            'inf.work_place_detail': project.get('work_place_detail', ''),
            'inf.work_place_water': project.get('work_place_water', ''),
            'inf.work_station': project.get('work_station', ''),
            'inf.work_name': project.get('work_name', ''),
            'inf.work_start_date': project.get('work_start_date', ''),
            'inf.work_end_date': project.get('work_end_date', ''),
            'inf.job_length': project.get('job_length', 0),
            'inf.job_cost': project.get('job_cost', 0),
            'coords.2.lat': lat,
            'coords.2.lon': lon,
        }
        filtered_records.append(filtered_record)
    
    return pd.DataFrame(filtered_records)
