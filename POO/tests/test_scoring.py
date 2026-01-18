import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from digital_eye_fatigue_analyzer import EyeFatigueAnalyzer


class TestEyeFatigueAnalyzer(unittest.TestCase):
    """Unit tests for EyeFatigueAnalyzer class"""

    def setUp(self):
        """Initialize analyzer for tests"""
        self.analyzer = EyeFatigueAnalyzer()

    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.face_mesh)
        self.assertEqual(self.analyzer.fatigue_model, 'eyes-bhltc/1')
        self.assertEqual(self.analyzer.dryness_model, 'dry-eye-prediction/3')

    def test_redness_score_range(self):
        """Test that redness score returns value between 1 and 10"""
        # Mock a face detection failure - should return default 5
        import cv2
        import numpy as np
        
        # Create a dummy image (would fail face detection)
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        score = self.analyzer.get_redness(dummy_image)
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_dryness_score_range(self):
        """Test that dryness score returns value between 1 and 10"""
        # Test with non-existent file - should return default 5
        score = self.analyzer.get_dryness('/path/does/not/exist.jpg')
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_fatigue_score_range(self):
        """Test that fatigue score returns value between 1 and 10"""
        # Test with non-existent file - should return default 5
        score = self.analyzer.get_fatigue('/path/does/not/exist.jpg')
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_analyze_image_structure(self):
        """Test that analyze_image returns correct structure"""
        result = self.analyzer.analyze_image('/path/does/not/exist.jpg')
        
        self.assertIsInstance(result, dict)
        self.assertIn('redness', result)
        self.assertIn('dryness', result)
        self.assertIn('fatigue', result)
        self.assertIn('success', result)

    def test_all_scores_in_valid_range(self):
        """Test that all scores are always between 1 and 10"""
        result = self.analyzer.analyze_image('/path/does/not/exist.jpg')
        
        for score_name in ['redness', 'dryness', 'fatigue']:
            score = result[score_name]
            self.assertIsInstance(score, int)
            self.assertGreaterEqual(score, 1, f'{score_name} score below minimum')
            self.assertLessEqual(score, 10, f'{score_name} score above maximum')


if __name__ == '__main__':
    unittest.main()
