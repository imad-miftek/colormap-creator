/**
 * Colormap class for managing colormap functionality
 */
class Colormap {
    constructor() {
        this.colorStops = [];
        this.selectedStopIndex = -1;
        this.canvas = null;
        this.ctx = null;
    }

    /**
     * Initialize the colormap with default stops
     */
    initialize(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas dimensions to match its display size
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        
        // Add default color stops (black to white)
        this.colorStops = [
            { position: 0, color: '#000000' },
            { position: 1, color: '#ffffff' }
        ];
        
        this.render();
        return this;
    }
    
    /**
     * Render the colormap on the canvas
     */
    render() {
        if (!this.ctx) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        
        // Sort stops by position
        this.colorStops.sort((a, b) => a.position - b.position);
        
        // Create gradient
        const gradient = this.ctx.createLinearGradient(0, 0, width, 0);
        
        // Add color stops to gradient
        for (const stop of this.colorStops) {
            gradient.addColorStop(stop.position, stop.color);
        }
        
        // Fill with gradient
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, width, height);
        
        return this;
    }
    
    /**
     * Add a new color stop
     */
    addColorStop(position, color) {
        // Check if position is already occupied
        const existingPositions = this.colorStops.map(stop => stop.position);
        if (existingPositions.some(pos => Math.abs(pos - position) < 0.001)) {
            console.warn(`Position ${position} is already occupied`);
            return false;
        }
        
        this.colorStops.push({ position, color });
        this.render();
        return true;
    }
    
    /**
     * Remove a color stop by index
     */
    removeColorStop(index) {
        // Don't allow removing first or last stop
        if (index <= 0 || index >= this.colorStops.length - 1) {
            console.warn('Cannot remove first or last color stop');
            return false;
        }
        
        this.colorStops.splice(index, 1);
        if (this.selectedStopIndex === index) {
            this.selectedStopIndex = -1;
        } else if (this.selectedStopIndex > index) {
            this.selectedStopIndex--;
        }
        
        this.render();
        return true;
    }
    
    /**
     * Update a color stop
     */
    updateColorStop(index, position, color) {
        if (index < 0 || index >= this.colorStops.length) {
            console.warn(`Invalid stop index: ${index}`);
            return false;
        }
        
        // Don't allow moving first or last stop
        if ((index === 0 || index === this.colorStops.length - 1) && position !== undefined) {
            console.warn('Cannot move first or last color stop');
            return false;
        }
        
        const stop = this.colorStops[index];
        
        if (position !== undefined) {
            // Check bounds (don't allow moving outside neighboring stops)
            if (index > 0 && position < this.colorStops[index - 1].position) {
                position = this.colorStops[index - 1].position;
            }
            if (index < this.colorStops.length - 1 && position > this.colorStops[index + 1].position) {
                position = this.colorStops[index + 1].position;
            }
            
            stop.position = position;
        }
        
        if (color !== undefined) {
            stop.color = color;
        }
        
        this.render();
        return true;
    }
    
    /**
     * Get the color at a specific position
     */
    getColorAt(position) {
        // Ensure position is in range [0, 1]
        position = Math.max(0, Math.min(1, position));
        
        // Sort stops by position
        const stops = [...this.colorStops].sort((a, b) => a.position - b.position);
        
        // Handle edge cases
        if (position <= stops[0].position) return stops[0].color;
        if (position >= stops[stops.length - 1].position) return stops[stops.length - 1].color;
        
        // Find the stops before and after the position
        let beforeStop = stops[0];
        let afterStop = stops[stops.length - 1];
        
        for (let i = 0; i < stops.length - 1; i++) {
            if (stops[i].position <= position && stops[i + 1].position >= position) {
                beforeStop = stops[i];
                afterStop = stops[i + 1];
                break;
            }
        }
        
        // Calculate interpolation factor
        const range = afterStop.position - beforeStop.position;
        const factor = (position - beforeStop.position) / range;
        
        // Interpolate color
        return this.interpolateColor(beforeStop.color, afterStop.color, factor);
    }
    
    /**
     * Interpolate between two colors
     */
    interpolateColor(color1, color2, factor) {
        // Parse colors
        const r1 = parseInt(color1.substring(1, 3), 16);
        const g1 = parseInt(color1.substring(3, 5), 16);
        const b1 = parseInt(color1.substring(5, 7), 16);
        
        const r2 = parseInt(color2.substring(1, 3), 16);
        const g2 = parseInt(color2.substring(3, 5), 16);
        const b2 = parseInt(color2.substring(5, 7), 16);
        
        // Interpolate
        const r = Math.round(r1 + factor * (r2 - r1));
        const g = Math.round(g1 + factor * (g2 - g1));
        const b = Math.round(b1 + factor * (b2 - b1));
        
        // Convert back to hex
        return `#${(r).toString(16).padStart(2, '0')}${
            (g).toString(16).padStart(2, '0')}${
            (b).toString(16).padStart(2, '0')}`;
    }
    
    /**
     * Get the RGB values for a specific number of points
     */
    getRgbValues(numPoints) {
        const positions = Array.from({length: numPoints}, (_, i) => i / (numPoints - 1));
        return positions.map(pos => {
            const color = this.getColorAt(pos);
            const r = parseInt(color.substring(1, 3), 16);
            const g = parseInt(color.substring(3, 5), 16);
            const b = parseInt(color.substring(5, 7), 16);
            return { position: pos, rgb: [r, g, b], hex: color };
        });
    }
    
    /**
     * Export colormap as JSON
     */
    toJSON() {
        return {
            colorStops: this.colorStops,
            metadata: {
                version: '1.0',
                name: 'Custom Colormap',
                created: new Date().toISOString()
            }
        };
    }
    
    /**
     * Import colormap from JSON
     */
    fromJSON(json) {
        if (json && json.colorStops && Array.isArray(json.colorStops)) {
            this.colorStops = json.colorStops;
            this.selectedStopIndex = -1;
            this.render();
            return true;
        }
        return false;
    }
    
    /**
     * Export colormap as Python code
     */
    toPythonCode(name = 'custom_colormap') {
        // Sort stops by position
        const stops = [...this.colorStops].sort((a, b) => a.position - b.position);
        
        // Generate 512 RGB values for full colormap
        const rgbValues = this.getRgbValues(512);
        
        let code = `from plotpy.widgets.colormap.widget import EditableColormap
from qwt import QwtLinearColorMap
import numpy as np

# Color positions and RGB values
color_positions = [
`;
        
        // Add color stops
        for (const stop of stops) {
            const color = stop.color;
            const r = parseInt(color.substring(1, 3), 16);
            const g = parseInt(color.substring(3, 5), 16);
            const b = parseInt(color.substring(5, 7), 16);
            code += `    ${stop.position.toFixed(6)},  # (${r}, ${g}, ${b})\n`;
        }
        
        code += `]

# RGB color values (0-1 scale)
rgb_colors = [
`;
        
        // Add RGB colors
        for (const stop of stops) {
            const color = stop.color;
            const r = parseInt(color.substring(1, 3), 16) / 255;
            const g = parseInt(color.substring(3, 5), 16) / 255;
            const b = parseInt(color.substring(5, 7), 16) / 255;
            code += `    [${r.toFixed(6)}, ${g.toFixed(6)}, ${b.toFixed(6)}],\n`;
        }
        
        code += `]

# Create the colormap
def create_colormap(name='${name}'):
    # Create base colormap with first and last color
    color1_rgb = ${parseInt(stops[0].color.substring(1), 16)}
    color2_rgb = ${parseInt(stops[stops.length - 1].color.substring(1), 16)}
    colormap = EditableColormap(color1_rgb, color2_rgb, name=name)

    # Add intermediate color stops
`;
        
        // Add intermediate stops
        for (let i = 1; i < stops.length - 1; i++) {
            const color = stops[i].color;
            const rgb = parseInt(color.substring(1), 16);
            code += `    colormap.addColorStop(${stops[i].position.toFixed(6)}, ${rgb})\n`;
        }
        
        code += `
    return colormap

# Full 512 RGB values for the colormap
def get_rgb_array():
    return np.array([
`;
        
        // Add full RGB values
        for (const val of rgbValues) {
            code += `        [${val.rgb[0]}, ${val.rgb[1]}, ${val.rgb[2]}],\n`;
        }
        
        code += `    ])

# 512 position values corresponding to the RGB colors (0.0 to 1.0)
def get_positions():
    return np.array([
`;
        
        // Write positions in groups of 10 for readability
        for (let i = 0; i < rgbValues.length; i += 10) {
            const group = rgbValues.slice(i, i + 10).map(v => v.position.toFixed(6));
            code += `        ${group.join(', ')},\n`;
        }
        
        code += `    ])

# Example usage
if __name__ == '__main__':
    colormap = create_colormap()
    # Use with PlotPy: item.set_color_map(colormap)
    
    # Get the RGB array and positions for custom usage
    rgb_values = get_rgb_array()
    positions = get_positions()
    # These can be used for custom color interpolation
    # Each rgb_values[i] corresponds to positions[i]
`;
        
        return code;
    }
} 