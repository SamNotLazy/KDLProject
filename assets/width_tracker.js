// This script runs after the Dash app's layout is loaded in the browser.

// We wrap everything in a function to ensure we don't pollute the global namespace.
(function() {
    // This function finds our target div and updates its text with the window's current width.
    function updateWidthDisplay() {
        const widthDisplayElement = document.getElementById('device-width-display');
        if (widthDisplayElement) {
            widthDisplayElement.innerText = `Device Available Width: ${window.innerWidth}px`;
        }
    }

    // We need to wait for the window to fully load to ensure the 'device-width-display' element exists.
    window.addEventListener('load', updateWidthDisplay);

    // We also want to update the width whenever the user resizes their browser window.
    window.addEventListener('resize', updateWidthDisplay);
})();