// JS para gestión de conteo de impresiones/escaneos/copias

$(document).ready(function() {
    // Al seleccionar equipo, cargar sus datos
    $('#equipo_id').on('change', function() {
        const equipoId = $(this).val();
        if (equipoId) {
            cargarDatosEquipo(equipoId);
        } else {
            limpiarDatosEquipo();
        }
    });

    // Calcular diferencias al cambiar contadores
    $('.contador-actual').on('input', function() {
        calcularDiferencias();
    });

    // Validar contadores al perder foco
    $('.contador-actual').on('blur', function() {
        validarContador($(this));
    });
});

// Cargar datos del equipo seleccionado
function cargarDatosEquipo(equipoId) {
    if (!equipoId) {
        limpiarDatosEquipo();
        return;
    }

    $('#equipoInfo').html('<i class="fas fa-spinner fa-spin me-2"></i>Cargando información del equipo...');
    $.when(
        $.get(`/api/equipos/${equipoId}`),
        $.get(`/api/equipos/${equipoId}/ultimo-conteo`)
    ).then(function(equipoResponse, conteoResponse) {
        const equipo = equipoResponse[0].data;
        const ultimoConteo = conteoResponse[0].data || null;

        // Mostrar info básica
        let infoEquipo = [];
        if (equipo.marca) infoEquipo.push(`<strong>Marca:</strong> ${equipo.marca}`);
        if (equipo.modelo) infoEquipo.push(`<strong>Modelo:</strong> ${equipo.modelo}`);
        if (equipo.numero_serie) infoEquipo.push(`<strong>Serie:</strong> ${equipo.numero_serie}`);
        if (equipo.ubicacion) infoEquipo.push(`<strong>Ubicación:</strong> ${equipo.ubicacion}`);
        $('#equipo_info').val(infoEquipo.join(' | '));

        // Actualizar contadores con el último registro
        if (ultimoConteo) {
            $('#contador_impresiones_anterior').val(ultimoConteo.contador_impresion_actual || 0);
            $('#contador_escaneos_anterior').val(ultimoConteo.contador_escaneo_actual || 0);
            $('#contador_copias_anterior').val(ultimoConteo.contador_copias_actual || 0);
            $('#fechaUltimoConteo').text(new Date(ultimoConteo.fecha_conteo).toLocaleDateString());
            $('#contador_impresiones_actual').val(ultimoConteo.contador_impresion_actual || 0);
            $('#contador_escaneos_actual').val(ultimoConteo.contador_escaneo_actual || 0);
            $('#contador_copias_actual').val(ultimoConteo.contador_copias_actual || 0);
        } else {
            $('#contador_impresiones_anterior').val(0);
            $('#contador_escaneos_anterior').val(0);
            $('#contador_copias_anterior').val(0);
            $('#fechaUltimoConteo').text('Nunca');
            $('#contador_impresiones_actual').val(0);
            $('#contador_escaneos_actual').val(0);
            $('#contador_copias_actual').val(0);
        }
        calcularDiferencias();

        // Estado del equipo y mantenimiento
        $('#estado_equipo').val(equipo.estado || 'operativo');
        $('#requiere_mantenimiento').prop('checked', !!equipo.requiere_mantenimiento).trigger('change');
        $('#problemas_detectados').val(equipo.ultimos_problemas || '');
        $('#equipoInfo').html(`<i class="fas fa-check-circle text-success me-2"></i>Equipo cargado correctamente`);
    }).fail(function(error) {
        console.error('Error al cargar datos del equipo:', error);
        mostrarError('No se pudieron cargar los datos del equipo. Intente nuevamente.');
        limpiarDatosEquipo();
    });
}

// Limpiar datos del equipo
function limpiarDatosEquipo() {
    $('#equipo_info').val('');
    $('#contador_impresiones_anterior, #contador_escaneos_anterior, #contador_copias_anterior').val(0);
    $('#contador_impresiones_actual, #contador_escaneos_actual, #contador_copias_actual').val('');
    $('#diferencia_impresiones, #diferencia_escaneos, #diferencia_copias').text('0');
    $('#fechaUltimoConteo').text('Nunca');
    $('#estado_equipo').val('operativo');
    $('#requiere_mantenimiento').prop('checked', false).trigger('change');
    $('#problemas_detectados').val('');
    $('#equipoInfo').html('Seleccione un equipo para ver detalles');
}

// Calcula diferencias entre contadores actuales y anteriores
function calcularDiferencias() {
    // Valores actuales
    const impresionesActual = parseInt($('#contador_impresiones_actual').val()) || 0;
    const escaneosActual = parseInt($('#contador_escaneos_actual').val()) || 0;
    const copiasActual = parseInt($('#contador_copias_actual').val()) || 0;
    // Valores anteriores
    const impresionesAnterior = parseInt($('#contador_impresiones_anterior').val()) || 0;
    const escaneosAnterior = parseInt($('#contador_escaneos_anterior').val()) || 0;
    const copiasAnterior = parseInt($('#contador_copias_anterior').val()) || 0;

    // Calcular diferencias (no permitir negativos)
    const difImpresiones = Math.max(0, impresionesActual - impresionesAnterior);
    const difEscaneos = Math.max(0, escaneosActual - escaneosAnterior);
    const difCopias = Math.max(0, copiasActual - copiasAnterior);

    $('#diferencia_impresiones').text(difImpresiones);
    $('#diferencia_escaneos').text(difEscaneos);
    $('#diferencia_copias').text(difCopias);

    // Resaltar si el actual es menor al anterior
    resaltarContadorInvalido($('#contador_impresiones_actual'), impresionesActual, impresionesAnterior);
    resaltarContadorInvalido($('#contador_escaneos_actual'), escaneosActual, escaneosAnterior);
    resaltarContadorInvalido($('#contador_copias_actual'), copiasActual, copiasAnterior);
}

// Resalta campo si el valor actual es inválido
function resaltarContadorInvalido($elemento, valorActual, valorAnterior) {
    if (valorActual > 0 && valorActual < valorAnterior) {
        $elemento.addClass('is-invalid');
        if ($elemento.next('.invalid-feedback').length === 0) {
            $elemento.after('<div class="invalid-feedback d-block">El contador no puede ser menor que el registro anterior. Si hubo un reinicio, contacte al administrador.</div>');
        }
    } else {
        $elemento.removeClass('is-invalid');
        $elemento.nextAll('.invalid-feedback').remove();
    }
}

// Validación al perder foco
function validarContador($input) {
    const valor = parseInt($input.val()) || 0;
    const campo = $input.attr('id').replace('_actual', '');
    const valorAnterior = parseInt($(`#${campo}_anterior`).val()) || 0;

    if (valor < 0) {
        $input.val(0);
        calcularDiferencias();
        return false;
    }
    if (valor > 0 && valor < valorAnterior) {
        mostrarAdvertencia('El contador no puede ser menor que el registro anterior. Si hubo un reinicio, contacte al administrador.');
        $input.focus();
        return false;
    }
    return true;
}

// Mensaje de error
function mostrarError(mensaje) {
    Swal.fire({
        title: 'Error',
        text: mensaje,
        icon: 'error',
        confirmButtonText: 'Entendido'
    });
}

// Mensaje de advertencia
function mostrarAdvertencia(mensaje) {
    Swal.fire({
        title: 'Advertencia',
        text: mensaje,
        icon: 'warning',
        confirmButtonText: 'Entendido'
    });
}