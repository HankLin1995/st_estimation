"""
API Client for Backend Integration
Handles all communication with the FastAPI backend
"""
import requests
import streamlit as st
import os
from typing import Dict, List, Optional


class APIClient:
    """Client for interacting with the backend API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.timeout = 10
    
    def _handle_response(self, response: requests.Response, error_msg: str):
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                st.error(f"{error_msg}: 資料格式錯誤")
            elif response.status_code == 404:
                st.error(f"{error_msg}: 找不到資料")
            else:
                st.error(f"{error_msg}: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"{error_msg}: 連線錯誤 - {str(e)}")
            return None
    
    # Project APIs
    def create_project(self, project_data: Dict) -> Optional[Dict]:
        """Create a new project"""
        try:
            url = f"{self.base_url}/api/projects/"
            response = requests.post(url, json=project_data, timeout=self.timeout)
            return self._handle_response(response, "建立專案失敗")
        except Exception as e:
            st.error(f"建立專案時發生錯誤: {str(e)}")
            return None
    
    def get_projects(self, skip: int = 0, limit: int = 100, 
                    work_place: str = None, work_manage: str = None, 
                    work_station: str = None) -> Optional[List[Dict]]:
        """Get list of projects with optional filters"""
        try:
            url = f"{self.base_url}/api/projects/"
            params = {"skip": skip, "limit": limit}
            if work_place:
                params["work_place"] = work_place
            if work_manage:
                params["work_manage"] = work_manage
            if work_station:
                params["work_station"] = work_station
            
            response = requests.get(url, params=params, timeout=self.timeout)
            return self._handle_response(response, "取得專案列表失敗")
        except Exception as e:
            st.error(f"取得專案列表時發生錯誤: {str(e)}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get a specific project by ID"""
        try:
            url = f"{self.base_url}/api/projects/{project_id}"
            response = requests.get(url, timeout=self.timeout)
            return self._handle_response(response, "取得專案失敗")
        except Exception as e:
            st.error(f"取得專案時發生錯誤: {str(e)}")
            return None
    
    def update_project(self, project_id: int, project_data: Dict) -> Optional[Dict]:
        """Update an existing project"""
        try:
            url = f"{self.base_url}/api/projects/{project_id}"
            response = requests.put(url, json=project_data, timeout=self.timeout)
            return self._handle_response(response, "更新專案失敗")
        except Exception as e:
            st.error(f"更新專案時發生錯誤: {str(e)}")
            return None
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        try:
            url = f"{self.base_url}/api/projects/{project_id}"
            response = requests.delete(url, timeout=self.timeout)
            if response.status_code == 204:
                return True
            else:
                st.error(f"刪除專案失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            st.error(f"刪除專案時發生錯誤: {str(e)}")
            return False
    
    # Coordinate APIs
    def create_coordinate(self, coordinate_data: Dict) -> Optional[Dict]:
        """Create a new coordinate"""
        try:
            url = f"{self.base_url}/api/coordinates/"
            response = requests.post(url, json=coordinate_data, timeout=self.timeout)
            return self._handle_response(response, "建立座標失敗")
        except Exception as e:
            st.error(f"建立座標時發生錯誤: {str(e)}")
            return None
    
    def get_project_coordinates(self, project_id: int) -> Optional[List[Dict]]:
        """Get all coordinates for a project"""
        try:
            url = f"{self.base_url}/api/coordinates/project/{project_id}"
            response = requests.get(url, timeout=self.timeout)
            return self._handle_response(response, "取得座標列表失敗")
        except Exception as e:
            st.error(f"取得座標列表時發生錯誤: {str(e)}")
            return None
    
    def update_coordinate(self, coordinate_id: int, coordinate_data: Dict) -> Optional[Dict]:
        """Update an existing coordinate"""
        try:
            url = f"{self.base_url}/api/coordinates/{coordinate_id}"
            response = requests.put(url, json=coordinate_data, timeout=self.timeout)
            return self._handle_response(response, "更新座標失敗")
        except Exception as e:
            st.error(f"更新座標時發生錯誤: {str(e)}")
            return None
    
    def delete_coordinate(self, coordinate_id: int) -> bool:
        """Delete a coordinate"""
        try:
            url = f"{self.base_url}/api/coordinates/{coordinate_id}"
            response = requests.delete(url, timeout=self.timeout)
            if response.status_code == 204:
                return True
            else:
                st.error(f"刪除座標失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            st.error(f"刪除座標時發生錯誤: {str(e)}")
            return False
    
    # Image APIs
    def upload_image(self, project_id: int, image_type: str, file) -> Optional[Dict]:
        """Upload an image file"""
        try:
            url = f"{self.base_url}/api/images/upload/{project_id}"
            files = {"file": (file.name, file.getvalue(), file.type)}
            params = {"image_type": image_type}
            response = requests.post(url, files=files, params=params, timeout=30)
            return self._handle_response(response, "上傳圖片失敗")
        except Exception as e:
            st.error(f"上傳圖片時發生錯誤: {str(e)}")
            return None
    
    def create_image(self, image_data: Dict) -> Optional[Dict]:
        """Create a new image (metadata only)"""
        try:
            url = f"{self.base_url}/api/images/"
            response = requests.post(url, json=image_data, timeout=self.timeout)
            return self._handle_response(response, "建立圖片失敗")
        except Exception as e:
            st.error(f"建立圖片時發生錯誤: {str(e)}")
            return None
    
    def get_project_images(self, project_id: int, image_type: str = None) -> Optional[List[Dict]]:
        """Get all images for a project"""
        try:
            url = f"{self.base_url}/api/images/project/{project_id}"
            params = {}
            if image_type:
                params["image_type"] = image_type
            response = requests.get(url, params=params, timeout=self.timeout)
            return self._handle_response(response, "取得圖片列表失敗")
        except Exception as e:
            st.error(f"取得圖片列表時發生錯誤: {str(e)}")
            return None
    
    def update_image(self, image_id: int, image_data: Dict) -> Optional[Dict]:
        """Update an existing image"""
        try:
            url = f"{self.base_url}/api/images/{image_id}"
            response = requests.put(url, json=image_data, timeout=self.timeout)
            return self._handle_response(response, "更新圖片失敗")
        except Exception as e:
            st.error(f"更新圖片時發生錯誤: {str(e)}")
            return None
    
    def delete_image(self, image_id: int) -> bool:
        """Delete an image"""
        try:
            url = f"{self.base_url}/api/images/{image_id}"
            response = requests.delete(url, timeout=self.timeout)
            if response.status_code == 204:
                return True
            else:
                st.error(f"刪除圖片失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            st.error(f"刪除圖片時發生錯誤: {str(e)}")
            return False
    
    def get_image_file(self, image_id: int) -> Optional[bytes]:
        """Get image file content"""
        try:
            url = f"{self.base_url}/api/images/download/{image_id}"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            st.error(f"獲取圖片時發生錯誤: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """Check if backend API is healthy"""
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
