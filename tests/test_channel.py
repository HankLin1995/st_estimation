"""
渠道工程計算模組的單元測試
"""
import unittest
import sys
import os

# 添加父目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tabs.channel import (
    calculate_materials,
    calc_rebar_weight,
    get_wall_thickness,
    get_rebar_weight_loss
)

class TestChannelCalculations(unittest.TestCase):
    def test_wall_thickness(self):
        """測試牆身厚度計算"""
        test_cases = [
            (0.5, 0.2),   # 小於1.0m
            (1.0, 0.2),   # 等於1.0m
            (1.8, 0.2),   # 1.5-2.0m
            (2.2, 0.25),  # 2.0-2.5m
            (2.8, 0.3),   # 2.5-3.0m
            (3.5, 0.4),   # 大於3.0m
        ]
        
        for height, expected in test_cases:
            with self.subTest(height=height):
                self.assertEqual(get_wall_thickness(height), expected)

    def test_rebar_weight_loss(self):
        """測試鋼筋損耗計算"""
        test_cases = [
            (0, (0, 0)),        # 零根鋼筋
            (3, (0.559, 1.065)), # 3根鋼筋
            (4, (0.994, 1.065)), # 4根鋼筋
            (5, (1.56, 1.065)),  # 5根鋼筋
            (6, (2.24, 1.1)),    # 6根鋼筋
        ]
        
        for rebar_num, expected in test_cases:
            with self.subTest(rebar_num=rebar_num):
                self.assertEqual(get_rebar_weight_loss(rebar_num), expected)

    def test_calc_rebar_weight(self):
        """測試鋼筋重量計算"""
        # 測試案例：L1, L1_temp, L2, L2_temp, height
        test_cases = [
            # 簡單案例 (高度 < 1.0m)
            (2.0, 12, 2.0, 12, 0.8, 17.73),  # L1_num=4, L1_temp_num=3
            # 中等高度 (1.5-2.0m)
            (3.0, 17, 3.0, 17, 1.8, 54.96),  # L1_num=6, L1_temp_num=4
            # 較高牆身 (2.5-3.0m)
            (4.0, 22, 4.0, 22, 2.8, 108.70),  # L1_num=6, L1_temp_num=3, L2_num=5, L2_temp_num=3
        ]
        
        for L1, L1_temp, L2, L2_temp, height, expected in test_cases:
            with self.subTest(L1=L1, height=height):
                result = calc_rebar_weight(L1, L1_temp, L2, L2_temp, height)
                self.assertAlmostEqual(result, expected, places=2)

    def test_calculate_materials(self):
        """測試材料計算"""
        test_cases = [
            # (寬度, 高度, 預期結果)
            # 預期結果: (140混凝土體積, 210混凝土體積, 鋼筋重量, 模板A面積, 模板B面積)
            (1.0, 0.8, (0.16, 0.62, 17.73, 0, 5.2)),   # 低矮渠道
            (1.5, 1.8, (0.21, 1.12, 99.69, 8.6, 0)),   # 中等高度
            (2.0, 2.8, (0.28, 2.49, 108.70, 13.2, 0)),  # 較高渠道
        ]
        
        for width, height, expected in test_cases:
            with self.subTest(width=width, height=height):
                result = calculate_materials(width, height)
                # 檢查返回值的類型和數量
                self.assertEqual(len(result), 5)
                # 檢查各個值是否與預期相符
                for actual, exp in zip(result, expected):
                    self.assertAlmostEqual(actual, exp, places=2)

if __name__ == '__main__':
    unittest.main()
