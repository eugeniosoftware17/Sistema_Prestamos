document.addEventListener('DOMContentLoaded', () => {
    const nombreInput = document.getElementById('id_nombre');
    const direccionInput = document.getElementById('id_direccion');
    const telefonoInput = document.getElementById('id_telefono');
    const rncInput = document.getElementById('id_rnc');
    const emailInput = document.getElementById('id_email');
    const iconoInput = document.getElementById('id_icono');

    function actualizarTexto(input, ids, placeholder) {
        if (!input) return;
        const valor = input.value.trim() || placeholder;
        ids.forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.textContent = valor;
        });
    }

    function refrescarNombre() {
        actualizarTexto(nombreInput, ['preview-topbar-name', 'preview-doc-name'], 'Nombre del sistema');
        const letra = document.getElementById('icon-preview-letter');
        if (letra && nombreInput.value.trim()) {
            letra.textContent = nombreInput.value.trim().charAt(0).toUpperCase();
        }
    }

    if (nombreInput) nombreInput.addEventListener('input', refrescarNombre);
    if (direccionInput) {
        direccionInput.addEventListener('input', () =>
            actualizarTexto(direccionInput, ['preview-doc-direccion'], 'Dirección de la empresa')
        );
    }
    if (telefonoInput) {
        telefonoInput.addEventListener('input', () =>
            actualizarTexto(telefonoInput, ['preview-doc-telefono'], 'Teléfono')
        );
    }
    if (rncInput) {
        rncInput.addEventListener('input', () => {
            const el = document.getElementById('preview-doc-rnc');
            if (el) el.textContent = 'RNC: ' + (rncInput.value.trim() || '—');
        });
    }
    if (emailInput) {
        emailInput.addEventListener('input', () =>
            actualizarTexto(emailInput, ['preview-doc-email'], 'correo@empresa.com')
        );
    }

    if (iconoInput) {
        iconoInput.addEventListener('change', () => {
            const archivo = iconoInput.files[0];
            if (!archivo) return;

            const lector = new FileReader();
            lector.onload = (evento) => {
                const url = evento.target.result;
                mostrarImagen('icon-preview', url);
                mostrarImagen('preview-topbar-icon', url);
                mostrarImagen('preview-doc-icon', url);
            };
            lector.readAsDataURL(archivo);
        });
    }

    function mostrarImagen(contenedorId, url) {
        const contenedor = document.getElementById(contenedorId);
        if (!contenedor) return;
        contenedor.innerHTML = '';
        const img = document.createElement('img');
        img.src = url;
        img.alt = '';
        contenedor.appendChild(img);
    }
});
