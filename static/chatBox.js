
export class chatBox {
    constructor(m) {
        this.main = m;
        this.initializeSidebar();
    }

    initializeSidebar() {
        document.addEventListener('DOMContentLoaded', () => {
            const sidebarWidth = 250;
            const toggleButton = document.getElementById('toggle-sidebar');
            const userSidebar = document.getElementById('user-sidebar');
            
            toggleButton.style.right = `0px`; 
        
            toggleButton.addEventListener('click', () => {
                if (userSidebar.style.right === '0px') {
                    userSidebar.style.right = `-${sidebarWidth}px`;
                    toggleButton.style.right = `0px`;
                } else {
                    userSidebar.style.right = '0px';
                    toggleButton.style.right = `${sidebarWidth}px`;
                }
            });
        });        
    }
}
