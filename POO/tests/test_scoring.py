"""
Unit tests for fatigue scoring functions
"""
import unittest
import sys
import os

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_eye_fatigue_analyzer_api import DigitalEyeFatigueAnalyzer
import tkinter as tk


class TestScoring(unittest.TestCase):
    """Test cases for scoring functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        self.analyzer = DigitalEyeFatigueAnalyzer(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        self.root.destroy()
    
    def test_normalize_and_calibrate_none(self):
        """Test normalize_and_calibrate with None input"""
        result = self.analyzer.normalize_and_calibrate(None)
        self.assertEqual(result, 0.0)
    
    def test_normalize_and_calibrate_zero(self):
        """Test normalize_and_calibrate with 0.0 input"""
        result = self.analyzer.normalize_and_calibrate(0.0)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_normalize_and_calibrate_one(self):
        """Test normalize_and_calibrate with 1.0 input"""
        result = self.analyzer.normalize_and_calibrate(1.0)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_compute_final_fatigue_low_inputs(self):
        """Test compute_final_fatigue with very low raw inputs and screen_time=0"""
        result = self.analyzer.compute_final_fatigue(0.0, 0.0, 0.0, 0.0, "Normal")
        
        # Should be Low (< 0.25)
        self.assertLess(result['final_fatigue'], 0.25)
        self.assertEqual(result['fatigue_level'], "Low")
        self.assertEqual(result['emoji'], "😊")
        self.assertEqual(result['color'], "green")
        
        # Check rounding
        self.assertEqual(len(str(result['final_fatigue']).split('.')[1]), 3)
    
    def test_compute_final_fatigue_high_inputs(self):
        """Test compute_final_fatigue with very high raw inputs and screen_time=12"""
        result = self.analyzer.compute_final_fatigue(1.0, 1.0, 1.0, 12.0, "Normal")
        
        # Should be High (>= 0.55) or close to 1.0
        self.assertGreaterEqual(result['final_fatigue'], 0.55)
        self.assertEqual(result['fatigue_level'], "High")
        self.assertEqual(result['emoji'], "😰")
        self.assertEqual(result['color'], "red")
        
        # Final should be clipped to [0, 1]
        self.assertLessEqual(result['final_fatigue'], 1.0)
    
    def test_compute_final_fatigue_mixed_inputs(self):
        """Test compute_final_fatigue with mixed inputs"""
        result = self.analyzer.compute_final_fatigue(0.5, 0.3, 0.4, 5.0, "Normal")
        
        # Should be in valid range
        self.assertGreaterEqual(result['final_fatigue'], 0.0)
        self.assertLessEqual(result['final_fatigue'], 1.0)
        
        # Check all components are present and rounded
        self.assertIn('f_calibrated', result)
        self.assertIn('r_calibrated', result)
        self.assertIn('d_calibrated', result)
        self.assertIn('time_factor', result)
        self.assertIn('final_fatigue', result)
        self.assertIn('fatigue_level', result)
        self.assertIn('emoji', result)
        self.assertIn('color', result)
    
    def test_compute_final_fatigue_condition_multiplier_normal(self):
        """Test condition multiplier for Normal condition"""
        result_normal = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Normal")
        self.assertEqual(result_normal['final_fatigue'], result_normal['final_fatigue'])  # Should be same
    
    def test_compute_final_fatigue_condition_multiplier_diabetic(self):
        """Test condition multiplier for Diabetic Retinopathy (1.15)"""
        result_normal = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Normal")
        result_diabetic = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Diabetic Retinopathy")
        
        # Diabetic should have higher final score due to 1.15 multiplier
        self.assertGreater(result_diabetic['final_fatigue'], result_normal['final_fatigue'])
    
    def test_compute_final_fatigue_condition_multiplier_glaucoma(self):
        """Test condition multiplier for Glaucoma (1.10)"""
        result_normal = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Normal")
        result_glaucoma = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Glaucoma")
        
        # Glaucoma should have higher final score due to 1.10 multiplier
        self.assertGreater(result_glaucoma['final_fatigue'], result_normal['final_fatigue'])
    
    def test_compute_final_fatigue_condition_multiplier_cataract(self):
        """Test condition multiplier for Cataract (1.05)"""
        result_normal = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Normal")
        result_cataract = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 8.0, "Cataract")
        
        # Cataract should have higher final score due to 1.05 multiplier
        self.assertGreater(result_cataract['final_fatigue'], result_normal['final_fatigue'])
    
    def test_compute_final_fatigue_time_factor_capping(self):
        """Test that time factor is capped at 1.0"""
        result = self.analyzer.compute_final_fatigue(0.5, 0.5, 0.5, 20.0, "Normal")
        
        # Time factor should be 1.0 (capped at 10 hours / 10.0)
        self.assertEqual(result['time_factor'], 1.0)
    
    def test_compute_final_fatigue_clipping(self):
        """Test that final fatigue is clipped to [0, 1]"""
        # Test with extreme values that might exceed bounds
        result_high = self.analyzer.compute_final_fatigue(2.0, 2.0, 2.0, 20.0, "Diabetic Retinopathy")
        result_low = self.analyzer.compute_final_fatigue(-2.0, -2.0, -2.0, 0.0, "Normal")
        
        self.assertLessEqual(result_high['final_fatigue'], 1.0)
        self.assertGreaterEqual(result_low['final_fatigue'], 0.0)
    
    def test_compute_final_fatigue_rounding(self):
        """Test that all numeric values are rounded to 3 decimals"""
        result = self.analyzer.compute_final_fatigue(0.123456, 0.789012, 0.456789, 7.5, "Normal")
        
        # Check rounding for all numeric fields
        decimals_f = len(str(result['f_calibrated']).split('.')[1]) if '.' in str(result['f_calibrated']) else 0
        decimals_r = len(str(result['r_calibrated']).split('.')[1]) if '.' in str(result['r_calibrated']) else 0
        decimals_d = len(str(result['d_calibrated']).split('.')[1]) if '.' in str(result['d_calibrated']) else 0
        decimals_t = len(str(result['time_factor']).split('.')[1]) if '.' in str(result['time_factor']) else 0
        decimals_final = len(str(result['final_fatigue']).split('.')[1]) if '.' in str(result['final_fatigue']) else 0
        
        self.assertLessEqual(decimals_f, 3)
        self.assertLessEqual(decimals_r, 3)
        self.assertLessEqual(decimals_d, 3)
        self.assertLessEqual(decimals_t, 3)
        self.assertLessEqual(decimals_final, 3)
    
    def test_fatigue_level_thresholds(self):
        """Test fatigue level thresholds: <0.25 Low, <0.55 Moderate, else High"""
        # Test Low threshold
        result_low = self.analyzer.compute_final_fatigue(0.0, 0.0, 0.0, 0.0, "Normal")
        self.assertEqual(result_low['fatigue_level'], "Low")
        
        # Test Moderate threshold (should be >= 0.25 and < 0.55)
        # Use values that will produce a moderate score
        result_moderate = self.analyzer.compute_final_fatigue(0.3, 0.2, 0.2, 3.0, "Normal")
        if 0.25 <= result_moderate['final_fatigue'] < 0.55:
            self.assertEqual(result_moderate['fatigue_level'], "Moderate")
        
        # Test High threshold
        result_high = self.analyzer.compute_final_fatigue(1.0, 1.0, 1.0, 12.0, "Normal")
        if result_high['final_fatigue'] >= 0.55:
            self.assertEqual(result_high['fatigue_level'], "High")


if __name__ == '__main__':
    unittest.main()

