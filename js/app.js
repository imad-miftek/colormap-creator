/**
 * Colormap Creator App
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize colormap
    const colormap = new Colormap().initialize('colormap-canvas');
    
    // DOM elements
    const colorStopsContainer = document.getElementById('color-stops-container');
    const stopsTable = document.getElementById('stops-table').getElementsByTagName('tbody')[0];
    const rgbTable = document.getElementById('rgb-table').getElementsByTagName('tbody')[0];
    const addStopBtn = document.getElementById('add-stop-btn');
    const saveBtn = document.getElementById('save-btn');
    const loadBtn = document.getElementById('load-btn');
    const loadFile = document.getElementById('load-file');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Modal elements
    const addStopModal = document.getElementById('add-stop-modal');
    const closeModalBtn = addStopModal.querySelector('.close');
    const positionInput = document.getElementById('position-input');
    const colorMethodSelect = document.getElementById('color-method');
    const colorPicker = document.getElementById('color-picker');
    const colorPickerContainer = document.getElementById('color-picker-container');
    const addStopConfirmBtn = document.getElementById('add-stop-confirm');
    const addStopCancelBtn = document.getElementById('add-stop-cancel');
    
    // Context menu
    let contextMenu = null;
    let selectedStopElement = null;
    
    // Create context menu
    function createContextMenu() {
        if (contextMenu) {
            document.body.removeChild(contextMenu);
        }
        
        contextMenu = document.createElement('div');
        contextMenu.className = 'context-menu';
        
        const editColorItem = document.createElement('div');
        editColorItem.className = 'context-menu-item';
        editColorItem.textContent = 'Edit Color';
        editColorItem.onclick = editSelectedStopColor;
        
        const removeStopItem = document.createElement('div');
        removeStopItem.className = 'context-menu-item';
        removeStopItem.textContent = 'Remove Color Stop';
        removeStopItem.onclick = removeSelectedStop;
        
        contextMenu.appendChild(editColorItem);
        contextMenu.appendChild(removeStopItem);
        document.body.appendChild(contextMenu);
    }
    
    // Hide context menu
    function hideContextMenu() {
        if (contextMenu) {
            contextMenu.style.display = 'none';
        }
    }
    
    // Render color stops UI
    function renderColorStops() {
        // Clear container
        colorStopsContainer.innerHTML = '';
        
        // Create color stop elements
        colormap.colorStops.forEach((stop, index) => {
            const template = document.getElementById('color-stop-template');
            const stopElement = document.importNode(template.content, true).querySelector('.color-stop');
            
            stopElement.dataset.index = index;
            stopElement.style.left = `${stop.position * 100}%`;
            stopElement.querySelector('.color-handle').style.backgroundColor = stop.color;
            
            if (index === colormap.selectedStopIndex) {
                stopElement.classList.add('selected');
            }
            
            // Make the color stops draggable (except first and last)
            if (index > 0 && index < colormap.colorStops.length - 1) {
                stopElement.draggable = true;
                
                stopElement.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', index);
                    colormap.selectedStopIndex = index;
                    renderColorStops();
                });
                
                // Right-click for context menu
                stopElement.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    colormap.selectedStopIndex = index;
                    selectedStopElement = stopElement;
                    renderColorStops();
                    
                    if (!contextMenu) {
                        createContextMenu();
                    }
                    
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = `${e.pageX}px`;
                    contextMenu.style.top = `${e.pageY}px`;
                });
            }
            
            // Click to select
            stopElement.addEventListener('click', function(e) {
                colormap.selectedStopIndex = index;
                renderColorStops();
            });
            
            // Double-click to edit color
            stopElement.addEventListener('dblclick', function(e) {
                editStopColor(index);
            });
            
            colorStopsContainer.appendChild(stopElement);
        });
    }
    
    // Update stops table
    function updateStopsTable() {
        stopsTable.innerHTML = '';
        
        colormap.colorStops.forEach((stop, i) => {
            const row = stopsTable.insertRow();
            
            // Index
            const indexCell = row.insertCell();
            indexCell.textContent = i;
            
            // Position
            const positionCell = row.insertCell();
            positionCell.textContent = stop.position.toFixed(4);
            
            // Color
            const colorCell = row.insertCell();
            const colorDiv = document.createElement('div');
            colorDiv.className = 'color-cell';
            colorDiv.style.backgroundColor = stop.color;
            colorDiv.title = stop.color;
            colorCell.appendChild(colorDiv);
            
            // RGB
            const rgbCell = row.insertCell();
            const r = parseInt(stop.color.substring(1, 3), 16);
            const g = parseInt(stop.color.substring(3, 5), 16);
            const b = parseInt(stop.color.substring(5, 7), 16);
            rgbCell.textContent = `(${r}, ${g}, ${b})`;
            
            // Double-click color cell to edit
            colorCell.addEventListener('dblclick', function() {
                editStopColor(i);
            });
        });
    }
    
    // Update RGB values table
    function updateRgbTable() {
        rgbTable.innerHTML = '';
        
        // Get 512 RGB values
        const rgbValues = colormap.getRgbValues(512);
        
        rgbValues.forEach((val, i) => {
            const row = rgbTable.insertRow();
            
            // Index
            const indexCell = row.insertCell();
            indexCell.textContent = i;
            
            // Position
            const positionCell = row.insertCell();
            positionCell.textContent = val.position.toFixed(4);
            
            // Color
            const colorCell = row.insertCell();
            const colorDiv = document.createElement('div');
            colorDiv.className = 'color-cell';
            colorDiv.style.backgroundColor = val.hex;
            colorDiv.title = val.hex;
            colorCell.appendChild(colorDiv);
            
            // RGB
            const rgbCell = row.insertCell();
            rgbCell.textContent = `(${val.rgb[0]}, ${val.rgb[1]}, ${val.rgb[2]})`;
        });
    }
    
    // Update all UI
    function updateUI() {
        renderColorStops();
        updateStopsTable();
        updateRgbTable();
    }
    
    // Edit color stop
    function editStopColor(index) {
        const stop = colormap.colorStops[index];
        const color = stop.color;
        
        // Use jscolor
        const picker = new jscolor(document.createElement('input'));
        picker.fromString(color.substring(1)); // Remove # from hex
        picker.onFineChange = function() {
            const newColor = '#' + picker.toString();
            colormap.updateColorStop(index, undefined, newColor);
            updateUI();
        };
        picker.show();
    }
    
    // Edit selected stop color (from context menu)
    function editSelectedStopColor() {
        hideContextMenu();
        if (colormap.selectedStopIndex >= 0) {
            editStopColor(colormap.selectedStopIndex);
        }
    }
    
    // Remove selected stop
    function removeSelectedStop() {
        hideContextMenu();
        if (colormap.selectedStopIndex > 0 && colormap.selectedStopIndex < colormap.colorStops.length - 1) {
            colormap.removeColorStop(colormap.selectedStopIndex);
            updateUI();
        }
    }
    
    // Handle color stops container click to add new stop
    colorStopsContainer.addEventListener('click', function(e) {
        // Ignore clicks on stops themselves
        if (e.target.closest('.color-stop')) {
            return;
        }
        
        // Calculate position within container
        const rect = colorStopsContainer.getBoundingClientRect();
        const position = (e.clientX - rect.left) / rect.width;
        
        // Get interpolated color at that position
        const color = colormap.getColorAt(position);
        
        // Add color stop if valid position
        if (position >= 0 && position <= 1) {
            if (colormap.addColorStop(position, color)) {
                updateUI();
            }
        }
    });
    
    // Make color stops container a drop target
    colorStopsContainer.addEventListener('dragover', function(e) {
        e.preventDefault();
    });
    
    colorStopsContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        const index = parseInt(e.dataTransfer.getData('text/plain'));
        
        // Calculate new position
        const rect = colorStopsContainer.getBoundingClientRect();
        const position = (e.clientX - rect.left) / rect.width;
        
        // Update the stop position
        if (position >= 0 && position <= 1) {
            colormap.updateColorStop(index, position);
            updateUI();
        }
    });
    
    // Add color stop button
    addStopBtn.addEventListener('click', function() {
        // Reset modal inputs
        positionInput.value = '0.5';
        colorMethodSelect.value = 'choose';
        colorPickerContainer.style.display = 'block';
        
        // Initialize color picker
        if (!colorPicker.jscolor) {
            jscolor.install();
        }
        colorPicker.jscolor.fromString('FFFFFF');
        
        // Show modal
        addStopModal.style.display = 'block';
    });
    
    // Color method change
    colorMethodSelect.addEventListener('change', function() {
        colorPickerContainer.style.display = this.value === 'choose' ? 'block' : 'none';
    });
    
    // Add stop confirm
    addStopConfirmBtn.addEventListener('click', function() {
        const position = parseFloat(positionInput.value);
        let color;
        
        if (colorMethodSelect.value === 'choose') {
            color = '#' + colorPicker.jscolor.toString();
        } else {
            color = colormap.getColorAt(position);
        }
        
        if (colormap.addColorStop(position, color)) {
            updateUI();
            addStopModal.style.display = 'none';
        } else {
            alert('Could not add color stop. Position may already be occupied.');
        }
    });
    
    // Close modal
    function closeModal() {
        addStopModal.style.display = 'none';
    }
    
    closeModalBtn.addEventListener('click', closeModal);
    addStopCancelBtn.addEventListener('click', closeModal);
    
    window.addEventListener('click', function(e) {
        if (e.target === addStopModal) {
            closeModal();
        }
    });
    
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Remove active class from all buttons and content
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Save colormap
    saveBtn.addEventListener('click', function() {
        // Create menu for export format options
        const exportMenu = document.createElement('div');
        exportMenu.className = 'context-menu';
        
        const jsonOption = document.createElement('div');
        jsonOption.className = 'context-menu-item';
        jsonOption.textContent = 'Save as JSON';
        jsonOption.onclick = function() {
            saveAsJSON();
            document.body.removeChild(exportMenu);
        };
        
        const pyOption = document.createElement('div');
        pyOption.className = 'context-menu-item';
        pyOption.textContent = 'Save as Python Module';
        pyOption.onclick = function() {
            saveAsPython();
            document.body.removeChild(exportMenu);
        };
        
        exportMenu.appendChild(jsonOption);
        exportMenu.appendChild(pyOption);
        document.body.appendChild(exportMenu);
        
        // Position menu near the save button
        const rect = saveBtn.getBoundingClientRect();
        exportMenu.style.display = 'block';
        exportMenu.style.left = `${rect.left}px`;
        exportMenu.style.top = `${rect.bottom + 5}px`;
        
        // Close menu when clicking outside
        const clickHandler = function(e) {
            if (!exportMenu.contains(e.target) && e.target !== saveBtn) {
                document.body.removeChild(exportMenu);
                document.removeEventListener('click', clickHandler);
            }
        };
        
        setTimeout(() => {
            document.addEventListener('click', clickHandler);
        }, 0);
    });
    
    // Save as JSON
    function saveAsJSON() {
        const json = colormap.toJSON();
        const blob = new Blob([JSON.stringify(json, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'colormap.json';
        a.click();
        
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    // Save as Python
    function saveAsPython() {
        const name = prompt('Enter a name for the colormap:', 'custom_colormap');
        if (!name) return;
        
        const pythonCode = colormap.toPythonCode(name);
        const blob = new Blob([pythonCode], {type: 'text/plain'});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${name}.py`;
        a.click();
        
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    // Load colormap
    loadBtn.addEventListener('click', function() {
        loadFile.click();
    });
    
    loadFile.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const json = JSON.parse(e.target.result);
                if (colormap.fromJSON(json)) {
                    updateUI();
                } else {
                    alert('Invalid colormap file format');
                }
            } catch (err) {
                alert('Error loading colormap: ' + err.message);
            }
        };
        reader.readAsText(file);
        
        // Reset file input
        this.value = '';
    });
    
    // Close context menu when clicking elsewhere
    document.addEventListener('click', function(e) {
        if (contextMenu && !contextMenu.contains(e.target) && 
            (!selectedStopElement || !selectedStopElement.contains(e.target))) {
            hideContextMenu();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        // Update canvas dimensions
        colormap.canvas.width = colormap.canvas.offsetWidth;
        colormap.canvas.height = colormap.canvas.offsetHeight;
        colormap.render();
    });
    
    // Initialize UI
    createContextMenu();
    updateUI();
    
    // Hide context menu initially
    hideContextMenu();
}); 