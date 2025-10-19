module.exports = {
    content: [
        './MiCasillero/templates/**/*.html',
        './theme/templates/**/*.html',
        './**/templates/**/*.html',
        '!./**/node_modules',
        '!./node_modules',
        '!node_modules',
        './**/*.js',
        './**/*.py'
    ],
    darkMode: 'false',
    theme: {
        extend: {
            borderRadius: {
                DEFAULT: '2px',
            },
            // colors: {
            //     primary: '#008ad3',
            //     secondary: '#dedb0c',
            //     tertiary: '#a63ca3',
            //     foreground: '#cdcdcd',
            //     dark: '#000000',
            //     light: '#ffffff',
            // },
            darkMode: {
                'background': '#1a202c',
                'text': '#a0aec0',
            },
            fontFamily: {
                sans: ['Atkinson Hyperlegible', 'sans-serif'],
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('daisyui'),
    ],
    daisyui: {
        default: 'cupcake', // Default color theme for DaisyUI. 'light' or 'dark'.
        themes: [
            {
                azure:
                    {
                        primary: '#0078D4',
                        'primary-focus': '#0062ac',
                        'primary-content': '#ffffff',
                        'secondary': '#2B579A',
                        'secondary-focus': '#2c3e50',
                        'secondary-content': '#ffffff',
                        'accent': '#37cdbe',
                        'accent-focus': '#2aa79b',
                        'accent-content': '#ffffff',
                        'neutral': '#3d4451',
                        'neutral-focus': '#2a2e37',
                        'neutral-content': '#ffffff',
                        'base-100': '#ffffff',
                        'base-200': '#f9fafb',
                        'base-300': '#f4f5f7',
                        'base-content': '#1f2937',
                        'info': '#2094f3',
                        'success': '#009485',
                        'warning': '#ff9900',
                        'error': '#ff5724',
                        borderRadius: '2px',
                    },
            },
            "cupcake", "light", "dark", "bumblebee", "emerald",
            "corporate", "synthwave", "retro", "cyberpunk", "valentine",
            "halloween", "garden", "forest", "aqua", "lofi", "pastel",
            "fantasy", "wireframe", "black", "luxury", "dracula",
        ],
        darkTheme: "night",
        base: true,
        styled: true,
        utils: true,
        prefix: "",
        logs: true,
        themeRoot: ":root",
    },
}
