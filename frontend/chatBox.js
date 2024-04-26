// index.js
export class chatBox {
    constructor(m) {
        this.main = m;
        this.initializeSidebar();
    }

    initializeSidebar() {
        document.addEventListener('DOMContentLoaded', () => {
            const sidebarWidth = 300; // Width of the sidebar
            const toggleButton = document.getElementById('toggle-sidebar');
            const userSidebar = document.getElementById('user-sidebar');
        
            // Initially hide the sidebar
            userSidebar.style.right = `-${sidebarWidth}px`; // Sidebar is off-screen to the left
            toggleButton.style.right = `0px`; // Button is fully visible at the right edge of the viewport
        
            // Attach click event to toggle the sidebar
            toggleButton.addEventListener('click', () => {
                if (userSidebar.style.right === '0px') {
                    // Sidebar is visible, so hide it
                    userSidebar.style.right = `-${sidebarWidth}px`;
                    toggleButton.style.right = `0px`; // Return button to the viewport edge
                } else {
                    // Sidebar is hidden, so show it
                    userSidebar.style.right = '0px';
                    toggleButton.style.right = `${sidebarWidth}px`; // Move button to the external edge of the sidebar
                }
            });
        });        
    }
}
