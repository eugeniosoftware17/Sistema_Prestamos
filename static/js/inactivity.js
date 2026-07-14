(function () {
    const LIMITE_MS = 10 * 60 * 1000; // 10 minutos
    let temporizador;

    function cerrarSesion() {
        const formulario = document.getElementById('auto-logout-form');
        if (formulario) formulario.submit();
    }

    function reiniciarTemporizador() {
        clearTimeout(temporizador);
        temporizador = setTimeout(cerrarSesion, LIMITE_MS);
    }

    ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'].forEach((evento) => {
        document.addEventListener(evento, reiniciarTemporizador, { passive: true });
    });

    reiniciarTemporizador();
})();
