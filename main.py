import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
                              QFileDialog, QSplitter, QTabWidget, QColorDialog, QDialog, QFormLayout, QDoubleSpinBox, 
                              QDialogButtonBox, QComboBox, QMessageBox)
from PySide6.QtGui import QColor, QAction
from PySide6.QtCore import Qt
from plotpy.widgets.colormap.widget import ColorMapWidget, EditableColormap
from qwt import QwtInterval

def create_action(parent, title, triggered=None, icon=None, shortcut=None, tip=None):
    """Helper function to create a QAction"""
    action = QAction(title, parent)
    if triggered is not None:
        action.triggered.connect(triggered)
    if icon is not None:
        action.setIcon(icon)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    return action

class ColormapMakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colormap Maker")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create a splitter for the main areas
        splitter = QSplitter(Qt.Vertical)
        
        # Top area: ColorMap editor
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Create the colormap widget
        self.colormap_widget = ColorMapWidget(None, cmap_width=800, cmap_height=60)
        top_layout.addWidget(QLabel("Colormap Editor (Right-click to add/remove colors)"))
        top_layout.addWidget(self.colormap_widget)
        
        # Buttons for colormap operations
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Colormap")
        self.load_button = QPushButton("Load Colormap")
        self.add_stop_button = QPushButton("Add Color Stop")  # Add this line
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.add_stop_button)  # Add this line
        top_layout.addLayout(button_layout)
        
        # Bottom area: Tabs for data views
        bottom_widget = QTabWidget()
        
        # Tab 1: Color stops info
        self.stops_table = QTableWidget(0, 4)
        self.stops_table.setHorizontalHeaderLabels(["Index", "Position", "Hex Color", "RGB"])
        
        # Tab 2: Full RGB preview (512 values)
        self.rgb_preview = QTableWidget(0, 4)
        self.rgb_preview.setHorizontalHeaderLabels(["Index", "Position", "Hex Color", "RGB"])
        
        bottom_widget.addTab(self.stops_table, "Color Stops")
        bottom_widget.addTab(self.rgb_preview, "512 RGB Values")
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([200, 500])  # Set initial sizes
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Connect signals
        self.colormap_widget.COLORMAP_CHANGED.connect(self.update_tables)
        self.colormap_widget.HANDLE_ADDED.connect(self.update_tables)
        self.colormap_widget.HANDLE_DELETED.connect(self.update_tables)
        self.save_button.clicked.connect(self.save_colormap)
        self.load_button.clicked.connect(self.load_colormap)
        self.add_stop_button.clicked.connect(self.add_new_color_stop)  # Add this line
        
        # Add double-click event to the stops table to edit colors
        self.stops_table.cellClicked.connect(self.edit_color)
        
        # Also add a right-click context menu for the colormap widget
        # to edit colors of existing handles
        self.color_edit_action = create_action(
            self, 
            title="Edit color",
            icon=None,
            triggered=self.edit_selected_handle_color
        )
        self.colormap_widget.slider_menu.addAction(self.color_edit_action)
        
        # Initial update
        self.update_tables()
    
    def update_tables(self):
        # Update color stops table
        colormap = self.colormap_widget.get_colormap()
        stops = colormap.colorStops()
        
        # Clear and resize table
        self.stops_table.setRowCount(len(stops))
        
        # Fill table with color stop data
        for i, stop in enumerate(stops):
            pos = stop.pos
            color = QColor(stop.rgb)
            hex_color = color.name()
            rgb = f"({color.red()}, {color.green()}, {color.blue()})"
            
            # Add items to table
            self.stops_table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.stops_table.setItem(i, 1, QTableWidgetItem(f"{pos:.4f}"))
            
            # Create color cell
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            self.stops_table.setItem(i, 2, color_item)
            
            # RGB values
            self.stops_table.setItem(i, 3, QTableWidgetItem(rgb))
        
        self.stops_table.resizeColumnsToContents()
        
        # Update full RGB preview table (512 values)
        qwt_interval = QwtInterval(0, 1)
        rgb_values = []
        
        # Get 512 RGB values
        num_colors = 512
        self.rgb_preview.setRowCount(num_colors)
        
        for i in range(num_colors):
            pos = i / (num_colors - 1)
            rgb_int = colormap.rgb(qwt_interval, pos)
            color = QColor(rgb_int)
            hex_color = color.name()
            rgb = f"({color.red()}, {color.green()}, {color.blue()})"
            
            # Add items to table
            self.rgb_preview.setItem(i, 0, QTableWidgetItem(str(i)))
            self.rgb_preview.setItem(i, 1, QTableWidgetItem(f"{pos:.4f}"))
            
            # Create color cell
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            self.rgb_preview.setItem(i, 2, color_item)
            
            # RGB values
            self.rgb_preview.setItem(i, 3, QTableWidgetItem(rgb))
            
            # Save RGB values
            rgb_values.append((color.red(), color.green(), color.blue()))
    
    def save_colormap(self):
        """Save the colormap to a Python file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Colormap", "", "Python Files (*.py);;All Files (*)"
        )
        
        if not filename:
            return
            
        colormap = self.colormap_widget.get_colormap()
        stops = colormap.colorStops()
        
        with open(filename, 'w') as f:
            f.write("from plotpy.widgets.colormap.widget import EditableColormap\n")
            f.write("from qwt import QwtLinearColorMap\n")
            f.write("import numpy as np\n\n")
            
            # Write color positions and RGB values
            f.write("# Color positions and RGB values\n")
            f.write("color_positions = [\n")
            for stop in stops:
                color = QColor(stop.rgb)
                f.write(f"    {stop.pos:.6f},  # ({color.red()}, {color.green()}, {color.blue()})\n")
            f.write("]\n\n")
            
            f.write("# RGB color values (0-1 scale)\n")
            f.write("rgb_colors = [\n")
            for stop in stops:
                color = QColor(stop.rgb)
                f.write(f"    [{color.red()/255:.6f}, {color.green()/255:.6f}, {color.blue()/255:.6f}],\n")
            f.write("]\n\n")
            
            # Write colormap creation code
            f.write("# Create the colormap\n")
            f.write("def create_colormap(name='custom_colormap'):\n")
            f.write("    # Create base colormap with first and last color\n")
            first_color = QColor(stops[0].rgb)
            last_color = QColor(stops[-1].rgb)
            f.write(f"    color1_rgb = {first_color.rgb()}\n")
            f.write(f"    color2_rgb = {last_color.rgb()}\n")
            f.write("    colormap = EditableColormap(color1_rgb, color2_rgb, name=name)\n\n")
            
            # Add intermediate stops
            f.write("    # Add intermediate color stops\n")
            for i, stop in enumerate(stops[1:-1], 1):
                color = QColor(stop.rgb)
                f.write(f"    colormap.addColorStop({stop.pos:.6f}, {color.rgb()})\n")
            
            f.write("\n    return colormap\n\n")
            
            # Write 512 RGB values and their positions
            f.write("# Full 512 RGB values for the colormap\n")
            f.write("def get_rgb_array():\n")
            f.write("    return np.array([\n")
            
            # Generate 512 colors
            qwt_interval = QwtInterval(0, 1)
            rgb_values = []
            positions = []
            
            for i in range(512):
                pos = i / 511  # Range from 0.0 to 1.0
                positions.append(pos)
                rgb_int = colormap.rgb(qwt_interval, pos)
                color = QColor(rgb_int)
                f.write(f"        [{color.red()}, {color.green()}, {color.blue()}],\n")
                rgb_values.append([color.red(), color.green(), color.blue()])
            
            f.write("    ])\n\n")
            
            # Write 512 position values
            f.write("# 512 position values corresponding to the RGB colors (0.0 to 1.0)\n")
            f.write("def get_positions():\n")
            f.write("    return np.array([\n")
            
            # Write in groups of 10 for readability
            for i in range(0, 512, 10):
                group = positions[i:i+10]
                line = ", ".join(f"{pos:.6f}" for pos in group)
                f.write(f"        {line},\n")
            
            f.write("    ])\n\n")
            
            # Add example usage
            f.write("# Example usage\n")
            f.write("if __name__ == '__main__':\n")
            f.write("    colormap = create_colormap()\n")
            f.write("    # Use with PlotPy: item.set_color_map(colormap)\n")
            f.write("    \n")
            f.write("    # Get the RGB array and positions for custom usage\n")
            f.write("    rgb_values = get_rgb_array()\n")
            f.write("    positions = get_positions()\n")
            f.write("    # These can be used for custom color interpolation\n")
            f.write("    # Each rgb_values[i] corresponds to positions[i]\n")
    
    def load_colormap(self):
        """Load a colormap from a Python file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Colormap", "", "Python Files (*.py);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            # Create a temporary module name based on the file path
            import importlib.util
            import os
            
            # Create a module spec and load the module
            module_name = os.path.basename(filename).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has the create_colormap function
            if hasattr(module, 'create_colormap'):
                # Use the function to create the colormap
                colormap = module.create_colormap()
                self.colormap_widget.set_colormap(colormap)
                self.update_tables()
            else:
                # Alternatively, try to load from color_positions and rgb_colors
                # if they exist in the file
                if hasattr(module, 'color_positions') and hasattr(module, 'rgb_colors'):
                    # Create a new colormap from the positions and colors
                    first_color = QColor.fromRgbF(
                        module.rgb_colors[0][0], 
                        module.rgb_colors[0][1], 
                        module.rgb_colors[0][2]
                    )
                    last_color = QColor.fromRgbF(
                        module.rgb_colors[-1][0], 
                        module.rgb_colors[-1][1], 
                        module.rgb_colors[-1][2]
                    )
                    
                    # Create the colormap
                    colormap = EditableColormap(first_color, last_color)
                    
                    # Add intermediate stops
                    for i in range(1, len(module.color_positions) - 1):
                        pos = module.color_positions[i]
                        r, g, b = module.rgb_colors[i]
                        color = QColor.fromRgbF(r, g, b)
                        colormap.addColorStop(pos, color.rgb())
                    
                    self.colormap_widget.set_colormap(colormap)
                    self.update_tables()
                else:
                    raise ValueError("File does not contain valid colormap data")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Colormap",
                f"Failed to load colormap from file:\n{str(e)}"
            )

    def edit_color(self, row, column):
        """Edit color when double-clicking on a color cell in the stops table"""
        if column == 2:  # Hex Color column
            colormap = self.colormap_widget.get_colormap()
            stops = colormap.colorStops()
            
            # Get current color
            current_color = QColor(stops[row].rgb)
            
            # Open color dialog
            new_color = QColorDialog.getColor(
                current_color, 
                self, 
                f"Select Color for Stop {row}"
            )
            
            # If user selected a valid color, update the stop
            if new_color.isValid():
                # Update the color in the colormap
                self.colormap_widget.edit_color_stop(row, None, new_color)
                self.update_tables()
    
    def edit_selected_handle_color(self):
        """Edit color of the currently selected handle from the context menu"""
        # Get the handle that was right-clicked (stored in _last_selection)
        x, _ = self.colormap_widget._last_selection
        x_value = self.colormap_widget.multi_range_hslider.widget_pos_to_value(x)
        
        # Find closest handle
        handle_index, _ = self.colormap_widget._get_closest_handle_index(x_value)
        
        # Get current color
        current_color = self.colormap_widget.get_handle_color(handle_index)
        
        # Open color dialog
        new_color = QColorDialog.getColor(
            current_color, 
            self, 
            f"Select Color for Handle {handle_index}"
        )
        
        # If user selected a valid color, update the handle
        if new_color.isValid():
            self.colormap_widget.edit_color_stop(handle_index, None, new_color)
            self.update_tables()

    def add_new_color_stop(self):
        """Add a new color stop at a specific position with a specific color"""
        # Create a custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Color Stop")
        layout = QFormLayout(dialog)
        
        # Position input
        position_spinner = QDoubleSpinBox()
        position_spinner.setRange(0.0, 1.0)
        position_spinner.setDecimals(4)
        position_spinner.setSingleStep(0.01)
        position_spinner.setValue(0.5)  # Default to middle
        layout.addRow("Position (0-1):", position_spinner)
        
        # Color input options
        color_method = QComboBox()
        color_method.addItems(["Choose Color", "Interpolate from Colormap"])
        layout.addRow("Color Method:", color_method)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        # Show dialog
        if dialog.exec() == QDialog.Accepted:
            position = position_spinner.value()
            
            # Check if position is already occupied
            colormap = self.colormap_widget.get_colormap()
            stops = colormap.colorStops()
            existing_positions = [stop.pos for stop in stops]
            
            if color_method.currentText() == "Choose Color":
                # Let user pick a color
                color = QColorDialog.getColor(
                    QColor(Qt.white), 
                    self,
                    "Select Color for New Stop"
                )
                
                if not color.isValid():
                    return
            else:
                # Interpolate color from existing colormap
                qwt_interval = QwtInterval(0, 1)
                color_int = colormap.rgb(qwt_interval, position)
                color = QColor(color_int)
            
            # Add the color stop
            self.colormap_widget.add_handle_at_relative_pos(position, color)
            self.update_tables()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColormapMakerApp()
    window.show()
    sys.exit(app.exec())