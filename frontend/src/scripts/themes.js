const themes = {
    "default": {
        "name": "Default",
        "background": "#ffffff",
        "text": "#000000",
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",     "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40"
    },
    "dark": {
        "name": "Dark",
        "background": "#343a40",
        "text": "#ffffff",
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#000000"
    }
};

export default themes;


function applyTheme(themeName) {
    const theme = themes[themeName] || themes["default"];
    document.documentElement.style.setProperty('--background-color', theme.background);
    document.documentElement.style.setProperty('--text-color', theme.text);
    document.documentElement.style.setProperty('--primary-color', theme.primary);
    document.documentElement.style.setProperty('--secondary-color', theme.secondary);
    document.documentElement.style.setProperty('--success-color', theme.success);
    document.documentElement.style.setProperty('--danger-color', theme.danger);
    document.documentElement.style.setProperty('--warning-color', theme.warning);
    document.documentElement.style.setProperty('--info-color', theme.info);
    document.documentElement.style.setProperty('--light-color', theme.light);
    document.documentElement.style.setProperty('--dark-color', theme.dark);
}

export { applyTheme };



function toggleTheme() {
    //Check the current theme and toggle between 'default' and 'dark'
    const currentTheme = localStorage.getItem('theme') || 'default';
    const newTheme = currentTheme === 'default' ? 'dark' : 'default';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'default';
    applyTheme(savedTheme);

    const themeToggleButton = document.querySelector('#theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }
});

export {toggleTheme};