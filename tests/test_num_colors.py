import sys
import os
import unittest
import tempfile
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtGui import QColor
import importlib.util
from unittest.mock import patch

# Add the parent directory to the path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import ColormapMakerApp

class TestNumColors(unittest.TestCase):
    """Test that saved colormaps respect the user-defined num_colors value."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication once for all tests."""
        cls.app = QApplication.instance() or QApplication([])
        
        # Create a temporary directory for test files
        cls.temp_dir = tempfile.mkdtemp()
    
    def setUp(self):
        """Set up a fresh colormap maker app for each test."""
        self.colormap_app = ColormapMakerApp()
    
    def tearDown(self):
        """Clean up after each test."""
        self.colormap_app.close()
    
    def test_save_respects_num_colors(self):
        """Test that the saved colormap respects the user-defined num_colors value."""
        # Set a custom number of colors
        custom_num_colors = 512
        self.colormap_app.num_colors = custom_num_colors
        self.colormap_app.update_tables()
        
        # Define a path for the test file
        test_file = os.path.join(self.temp_dir, "test_colormap.py")
        
        # Mock the QFileDialog.getSaveFileName to return our test file
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(test_file, "Python Files (*.py)")):
            # Save the colormap
            self.colormap_app.save_colormap()
        
        # Check that the file was created
        self.assertTrue(os.path.exists(test_file))
        
        # Import the saved module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that the module has the correct number of colors
        self.assertTrue(hasattr(module, f"_rgb_array_{custom_num_colors}"))
        self.assertTrue(hasattr(module, f"_positions_{custom_num_colors}"))
        
        # Check that the rgb array has the correct length
        rgb_array = getattr(module, f"_rgb_array_{custom_num_colors}")
        self.assertEqual(len(rgb_array), custom_num_colors)
        
        # Check that the positions array has the correct length
        positions = getattr(module, f"_positions_{custom_num_colors}")
        self.assertEqual(len(positions), custom_num_colors)
        
        # Check that the default num_colors in the module matches our custom value
        # Instead of checking string constants, let's check the function behavior
        # Call get_rgb_array with default parameters and verify the length
        default_rgb_array = module.get_rgb_array()
        self.assertEqual(len(default_rgb_array), custom_num_colors, 
                         f"Default num_colors should be {custom_num_colors}, but got {len(default_rgb_array)}")
        
        # Also check that we can specify a different number of colors
        custom_rgb_array = module.get_rgb_array(100)
        self.assertEqual(len(custom_rgb_array), 100)
        
        # Check the actual default value in the function definition
        # This is the key test to ensure the custom num_colors is saved as the default
        function_code = open(test_file, 'r').read()
        self.assertIn(f"num_colors = {custom_num_colors}", function_code, 
                      f"The default num_colors value in the saved file should be {custom_num_colors}")
    
    def test_color_accuracy(self):
        """Test that the saved RGB values match the original colormap."""
        # Add a specific color stop
        self.colormap_app.colormap_widget.add_handle_at_relative_pos(0.5, QColor(255, 0, 0))  # Red at middle
        
        # Define a path for the test file
        test_file = os.path.join(self.temp_dir, "test_color_accuracy.py")
        
        # Save the colormap
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(test_file, "Python Files (*.py)")):
            self.colormap_app.save_colormap()
        
        # Import the saved module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that the middle color is still red
        rgb_array = getattr(module, f"_rgb_array_{self.colormap_app.num_colors}")
        middle_index = self.colormap_app.num_colors // 2
        self.assertEqual(rgb_array[middle_index], [255, 0, 0])
    
    def test_load_colormap(self):
        """Test that loading a colormap preserves the color stops."""
        # Create a colormap with specific stops
        self.colormap_app.colormap_widget.add_handle_at_relative_pos(0.25, QColor(255, 0, 0))  # Red at 0.25
        self.colormap_app.colormap_widget.add_handle_at_relative_pos(0.75, QColor(0, 0, 255))  # Blue at 0.75
        
        # Define paths for the test files
        save_file = os.path.join(self.temp_dir, "test_save_load.py")
        
        # Save the colormap
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(save_file, "Python Files (*.py)")):
            self.colormap_app.save_colormap()
        
        # Create a new app instance
        new_app = ColormapMakerApp()
        
        # Load the colormap
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(save_file, "Python Files (*.py)")):
            new_app.load_colormap()
        
        # Get the colormap stops
        colormap = new_app.colormap_widget.get_colormap()
        stops = colormap.colorStops()
        
        # Check that we have at least 4 stops (start, 0.25, 0.75, end)
        self.assertGreaterEqual(len(stops), 4)
        
        # Find the stops at positions 0.25 and 0.75
        stop_025 = None
        stop_075 = None
        for stop in stops:
            if abs(stop.pos - 0.25) < 0.01:
                stop_025 = stop
            elif abs(stop.pos - 0.75) < 0.01:
                stop_075 = stop
        
        # Check that the stops were found
        self.assertIsNotNone(stop_025)
        self.assertIsNotNone(stop_075)
        
        # Check that the colors are correct
        self.assertEqual(QColor(stop_025.rgb).red(), 255)  # Red at 0.25
        self.assertEqual(QColor(stop_075.rgb).blue(), 255)  # Blue at 0.75
        
        # Clean up
        new_app.close()
    
    def test_min_max_colors(self):
        """Test with minimum and maximum color counts."""
        # Test with 16 colors (minimum)
        self.colormap_app.num_colors = 16
        self.colormap_app.update_tables()
        
        min_file = os.path.join(self.temp_dir, "test_min_colors.py")
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(min_file, "Python Files (*.py)")):
            self.colormap_app.save_colormap()
        
        # Import the saved module
        spec = importlib.util.spec_from_file_location("test_min", min_file)
        min_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(min_module)
        
        # Check that the arrays have 16 elements
        min_rgb_array = getattr(min_module, "_rgb_array_16")
        self.assertEqual(len(min_rgb_array), 16)
        
        # Test with 4096 colors (maximum)
        self.colormap_app.num_colors = 4096
        self.colormap_app.update_tables()
        
        max_file = os.path.join(self.temp_dir, "test_max_colors.py")
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(max_file, "Python Files (*.py)")):
            self.colormap_app.save_colormap()
        
        # Import the saved module
        spec = importlib.util.spec_from_file_location("test_max", max_file)
        max_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(max_module)
        
        # Check that the arrays have 4096 elements
        max_rgb_array = getattr(max_module, "_rgb_array_4096")
        self.assertEqual(len(max_rgb_array), 4096)

if __name__ == '__main__':
    unittest.main() 