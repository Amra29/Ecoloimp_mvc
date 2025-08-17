/**
 * Funcionalidad JavaScript para el módulo de Conteo de Impresiones
 * Maneja la interacción del formulario, validaciones y carga dinámica de datos
 */

$(document).ready(function() {
    // Variables globales
    let ultimoConteo = null;
    
    // Inicializar componentes
    inicializarSelect2();
    inicializarEventos();
    
    // Cargar datos iniciales si ya hay un equipo seleccionado
    if ($('#equipo_id').val()) {
        cargarDatosEquipo($('#equipo_id').val());
    }
    
    // Función para inicializar Select2
    function inicializarSelect2() {
        $('.select2').select2({
            theme: 'bootstrap4',
            width: '100%',
            placeholder: 'Seleccione una opción',
            allowClear: true,
            language: {
                noResults: function() {
                    return "No se encontraron resultados";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
    }
    
    // Función para inicializar eventos
    function inicializarEventos() {
        // Cargar sucursales al seleccionar cliente
        $('#cliente_id').on('change', function() {
            const clienteId = $(this).val();
            if (clienteId) {
                cargarSucursales(clienteId);
            } else {
                $('#sucursal_id').empty().trigger('change');
                $('#equipo_id').empty().trigger('change');
            }
        });
        
        // Cargar equipos al seleccionar sucursal
        $('#sucursal_id').on('change', function() {
            const sucursalId = $(this).val();
            if (sucursalId) {
                cargarEquipos(sucursalId);
            } else {
                $('#equipo_id').empty().trigger('change');
            }
        });
        
        // Cargar datos del equipo seleccionado
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
    }
    
    // Función para cargar sucursales de un cliente
    function cargarSucursales(clienteId) {
        if (!clienteId) return;
        
        $.ajax({
            url: `/api/clientes/${clienteId}/sucursales`,
            method: 'GET',
            dataType: 'json',
            beforeSend: function() {
                $('#sucursal_id').prop('disabled', true);
                $('#equipo_id').empty().trigger('change');
            },
            success: function(response) {
                const select = $('#sucursal_id');
                select.empty().append('<option value="">Seleccione una sucursal</option>');
                
                if (response.data && response.data.length > 0) {
                    $.each(response.data, function(index, sucursal) {
                        select.append(`<option value="${sucursal.id}">${sucursal.nombre}</option>`);
                    });
                }
                
                select.prop('disabled', false).trigger('change');
            },
            error: function(xhr, status, error) {
                console.error('Error al cargar sucursales:', error);
                mostrarError('No se pudieron cargar las sucursales. Intente nuevamente.');
                $('#sucursal_id').prop('disabled', false);
            }
        });
    }
    
    // Función para cargar equipos de una sucursal
    function cargarEquipos(sucursalId) {
        if (!sucursalId) return;
        
        $.ajax({
            url: `/api/sucursales/${sucursalId}/equipos`,
            method: 'GET',
            dataType: 'json',
            beforeSend: function() {
                $('#equipo_id').prop('disabled', true);
            },
            success: function(response) {
                const select = $('#equipo_id');
                select.empty().append('<option value="">Seleccione un equipo</option>');
                
                if (response.data && response.data.length > 0) {
                    $.each(response.data, function(index, equipo) {
                        select.append(`<option value="${equipo.id}">${equipo.marca} ${equipo.modelo} - ${equipo.numero_serie}</option>`);
                    });
                }
                
                select.prop('disabled', false).trigger('change');
            },
            error: function(xhr, status, error) {
                console.error('Error al cargar equipos:', error);
                mostrarError('No se pudieron cargar los equipos. Intente nuevamente.');
                $('#equipo_id').prop('disabled', false);
            }
        });
    }
    
    // Función para cargar datos del equipo seleccionado
    function cargarDatosEquipo(equipoId) {
        if (!equipoId) {
            limpiarDatosEquipo();
            return;
        }
        
        // Mostrar loading
        $('#equipoInfo').html('<i class="fas fa-spinner fa-spin me-2"></i>Cargando información del equipo...');
        
        // Obtener información del equipo
        $.when(
            $.get(`/api/equipos/${equipoId}`),
            $.get(`/api/equipos/${equipoId}/ultimo-conteo`)
        ).then(function(equipoResponse, conteoResponse) {
            // Procesar respuesta del equipo
            const equipo = equipoResponse[0].data;
            const ultimoConteo = conteoResponse[0].data || null;
            
            // Actualizar información del equipo
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
                
                // Establecer valores actuales ligeramente mayores que los anteriores
                $('#contador_impresiones_actual').val(ultimoConteo.contador_impresion_actual || 0);
                $('#contador_escaneos_actual').val(ultimoConteo.contador_escaneo_actual || 0);
                $('#contador_copias_actual').val(ultimoConteo.contador_copias_actual || 0);
                
                // Calcular diferencias iniciales
                calcularDiferencias();
            } else {
                // No hay conteos previos
                $('#contador_impresiones_anterior').val(0);
                $('#contador_escaneos_anterior').val(0);
                $('#contador_copias_anterior').val(0);
                $('#fechaUltimoConteo').text('Nunca');
                
                // Establecer valores iniciales en 0
                $('#contador_impresiones_actual').val(0);
                $('#contador_escaneos_actual').val(0);
                $('#contador_copias_actual').val(0);
                
                // Calcular diferencias iniciales
                calcularDiferencias();
            }
            
            // Actualizar estado del equipo
            if (equipo.estado) {
                $('#estado_equipo').val(equipo.estado);
            }
            
            // Actualizar información de mantenimiento si es necesario
            if (equipo.requiere_mantenimiento) {
                $('#requiere_mantenimiento').prop('checked', true).trigger('change');
                $('#problemas_detectados').val(equipo.ultimos_problemas || '');
            }
            
            // Actualizar información en el pie
            $('#equipoInfo').html(`<i class="fas fa-check-circle text-success me-2"></i>Equipo cargado correctamente`);
            
        }).fail(function(error) {
            console.error('Error al cargar datos del equipo:', error);
            mostrarError('No se pudieron cargar los datos del equipo. Intente nuevamente.');
            limpiarDatosEquipo();
        });
    }
    
    // Función para limpiar los datos del equipo
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
    
    // Función para calcular diferencias entre contadores actuales y anteriores
    function calcularDiferencias() {
        // Obtener valores actuales
        const impresionesActual = parseInt($('#contador_impresiones_actual').val()) || 0;
        const escaneosActual = parseInt($('#contador_escaneos_actual').val()) || 0;
        const copiasActual = parseInt($('#contador_copias_actual').val()) || 0;
        
        // Obtener valores anteriores
        const impresionesAnterior = parseInt($('#contador_impresiones_anterior').val()) || 0;
        const escaneosAnterior = parseInt($('#contador_escaneos_anterior').val()) || 0;
        const copiasAnterior = parseInt($('#contador_copias_anterior').val()) || 0;
        
        // Calcular diferencias
        const difImpresiones = Math.max(0, impresionesActual - impresionesAnterior);
        const difEscaneos = Math.max(0, escaneosActual - escaneosAnterior);
        const difCopias = Math.max(0, copiasActual - copiasAnterior);
        
        // Actualizar campos de diferencia
        $('#diferencia_impresiones').text(difImpresiones);
        $('#diferencia_escaneos').text(difEscaneos);
        $('#diferencia_copias').text(difCopias);
        
        // Resaltar si algún contador actual es menor que el anterior (excepto si es 0)
        resaltarContadorInvalido($('#contador_impresiones_actual'), impresionesActual, impresionesAnterior);
        resaltarContadorInvalido($('#contador_escaneos_actual'), escaneosActual, escaneosAnterior);
        resaltarContadorInvalido($('#contador_copias_actual'), copiasActual, copiasAnterior);
    }
    
    // Función para resaltar un contador inválido
    function resaltarContadorInvalido($elemento, valorActual, valorAnterior) {
        if (valorActual > 0 && valorActual < valorAnterior) {
            $elemento.addClass('is-invalid');
            $elemento.after('<div class="invalid-feedback d-block">El contador no puede ser menor que el registro anterior. Si hubo un reinicio, póngase en contacto con el administrador.</div>');
        } else {
            $elemento.removeClass('is-invalid');
            $elemento.nextAll('.invalid-feedback').remove();
        }
    }
    
    // Función para validar un contador al perder el foco
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
            mostrarAdvertencia('El contador no puede ser menor que el registro anterior. Si hubo un reinicio, póngase en contacto con el administrador.');
            $input.focus();
            return false;
        }
        
        return true;
    }
    
    // Función para mostrar mensajes de error
    function mostrarError(mensaje) {
        Swal.fire({
            title: 'Error',
            text: mensaje,
            icon: 'error',
            confirmButtonText: 'Entendido'
        });
    }
    
    // Función para mostrar advertencias
    function mostrarAdvertencia(mensaje) {
        Swal.fire({
            title: 'Advertencia',
            text: mensaje,
            icon: 'warning',
            confirmButtonText: 'Entendido'
        });
    }
    
    // Función para mostrar éxito
    function mostrarExito(mensaje) {
        Swal.fire({
            title: '¡Éxito!',
            text: mensaje,
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
    }
});
