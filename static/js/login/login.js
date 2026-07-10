document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.getElementById('password-toggle');
    
    // Contenedores de error
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');
    const generalError = document.getElementById('general-error');
    
    // Botón y Spinner
    const btnLogin = document.getElementById('btn-login');
    const btnText = btnLogin.querySelector('.btn-text');
    const loginSpinner = document.getElementById('login-spinner');

    /**
     * Alterna la visibilidad de la contraseña
     */
    passwordToggle.addEventListener('click', () => {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Cambiar el icono visual de forma dinámica (relleno del SVG)
        if (type === 'text') {
            passwordToggle.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-icon">
                    <line x1="1" y1="1" x2="23" y2="23"/>
                    <path d="M9 9a3 3 0 1 1-4.24-4.24"/>
                    <path d="M12 18a6 6 0 0 1-5-2.5"/>
                    <path d="M13.93 13.93A3 3 0 0 0 12 12a3 3 0 0 0-3 3c0 .73.27 1.4.71 1.91"/>
                    <path d="M1 12s4-8 11-8a9 9 0 0 1 6.36 2.64"/>
                    <path d="M23 12s-4 8-11 8a9.81 9.81 0 0 1-2.2-.28"/>
                </svg>
            `;
            passwordToggle.setAttribute('aria-label', 'Ocultar contraseña');
        } else {
            passwordToggle.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-icon">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
            `;
            passwordToggle.setAttribute('aria-label', 'Mostrar contraseña');
        }
    });

    /**
     * Limpia los errores de un campo específico
     */
    function clearError(inputElement, errorElement) {
        inputElement.closest('.input-group').classList.remove('has-error');
        errorElement.textContent = '';
        generalError.style.display = 'none';
    }

    // Limpieza dinámica mientras el usuario escribe
    usernameInput.addEventListener('input', () => clearError(usernameInput, usernameError));
    passwordInput.addEventListener('input', () => clearError(passwordInput, passwordError));

    /**
     * Valida en el cliente y, si todo está bien, deja que el formulario
     * se envíe de forma normal (POST) a la vista de login de Django.
     */
    loginForm.addEventListener('submit', (e) => {
        let isValid = true;
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        // Validar campo usuario
        if (!username) {
            e.preventDefault();
            usernameInput.closest('.input-group').classList.add('has-error');
            usernameError.textContent = 'El usuario o correo electrónico es obligatorio.';
            isValid = false;
        } else if (username.length < 4) {
            e.preventDefault();
            usernameInput.closest('.input-group').classList.add('has-error');
            usernameError.textContent = 'El usuario debe tener al menos 4 caracteres.';
            isValid = false;
        }

        // Validar campo contraseña
        if (!password) {
            e.preventDefault();
            passwordInput.closest('.input-group').classList.add('has-error');
            passwordError.textContent = 'La contraseña es obligatoria.';
            isValid = false;
        } else if (password.length < 6) {
            e.preventDefault();
            passwordInput.closest('.input-group').classList.add('has-error');
            passwordError.textContent = 'La contraseña debe tener al menos 6 caracteres.';
            isValid = false;
        }

        if (!isValid) return;

        // Formulario válido: mostrar estado de carga y dejar que continúe el envío real al servidor
        btnText.style.display = 'none';
        loginSpinner.style.display = 'block';
        btnLogin.setAttribute('disabled', 'true');
    });
});
