# Colormap Creator

A web-based tool for creating and editing colormaps, designed for use as an internal company tool. This application allows you to create custom colormaps with precise control over color stops and positions, and export them in formats compatible with Python visualization libraries.

## Features

- Interactive colormap editor with drag-and-drop color stops
- Add, remove, and edit color stops with precise control
- View color stop information in a tabular format
- Generate and view 512 RGB values for smooth gradients
- Export colormaps as JSON or Python code (compatible with PlotPy)
- Import previously saved colormaps from JSON
- Context menu for easy editing
- Mobile-responsive design

## Usage

### Accessing the Tool

This tool is hosted on GitHub Pages at: [https://your-username.github.io/colormap-creator/](https://your-username.github.io/colormap-creator/)

### Creating a Colormap

1. When you first open the tool, a default black-to-white colormap is created
2. Click on the colormap bar to add new color stops
3. Drag color stops to adjust their positions
4. Double-click or right-click on a color stop to edit its color
5. Use the "Add Color Stop" button to add a stop at a precise position

### Saving and Loading

- Click "Save Colormap" to export as JSON or Python code
- Click "Load Colormap" to import a previously saved JSON colormap

### Viewing Data

- Switch between "Color Stops" and "512 RGB Values" tabs to view detailed information
- Each table shows the position, color, and RGB values

## Technical Information

### How it Works

The colormap editor uses HTML Canvas for rendering and JavaScript for interactive functionality. Color interpolation is handled mathematically to ensure smooth gradients between color stops.

When exporting as Python code, the application generates code compatible with PlotPy's EditableColormap, making it easy to use in Python visualization projects.

### Used Libraries

- Chart.js - For rendering some UI elements
- JSColor - For the color picker functionality

### Browser Compatibility

- Chrome 60+
- Firefox 55+
- Edge 80+
- Safari 10+

## Development

### Project Structure

```
colormap-creator/
├── index.html          # Main HTML file
├── css/
│   └── style.css       # Styles for the application
├── js/
│   ├── app.js          # Main application logic
│   └── colormap.js     # Colormap class implementation
└── README.md           # This file
```

### Running Locally

To run the application locally:

1. Clone the repository
2. Open `index.html` in a web browser

No build steps or server required - it's a pure HTML/CSS/JS application.

## Deployment

This application is designed to be deployed on GitHub Pages:

1. Push the code to a GitHub repository
2. Enable GitHub Pages in the repository settings
3. Set the source to the branch containing your code

The application will be available at `https://[username].github.io/[repo-name]/`.

## License

Internal company use only. Not licensed for public distribution.

## Support

For issues or feature requests, please contact the development team. 