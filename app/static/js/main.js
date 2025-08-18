// JavaScript principal para el sistema de servicio técnico

// Import Bootstrap
var bootstrap = window.bootstrap

document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tooltips de Bootstrap
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Auto-ocultar alertas después de 5 segundos
  setTimeout(() => {
    var alerts = document.querySelectorAll(".alert")
    alerts.forEach((alert) => {
      var bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    })
  }, 5000)

  // Confirmación para eliminaciones
  var deleteButtons = document.querySelectorAll("[data-confirm-delete]")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      if (!confirm("¿Está seguro de que desea eliminar este elemento? Esta acción no se puede deshacer.")) {
        e.preventDefault()
      }
    })
  })

  // Cálculo automático de totales en facturas
  var subtotalInput = document.getElementById("subtotal")
  var impuestosInput = document.getElementById("impuestos")
  var totalInput = document.getElementById("total")

  if (subtotalInput && impuestosInput && totalInput) {
    function calcularTotal() {
      var subtotal = Number.parseFloat(subtotalInput.value) || 0
      var impuestos = Number.parseFloat(impuestosInput.value) || 0
      var total = subtotal + impuestos
      totalInput.value = total.toFixed(2)
    }

    subtotalInput.addEventListener("input", calcularTotal)
    impuestosInput.addEventListener("input", calcularTotal)
  }

  // Filtros dinámicos en tablas
  var searchInputs = document.querySelectorAll("[data-table-search]")
  searchInputs.forEach((input) => {
    input.addEventListener("input", function () {
      var filter = this.value.toLowerCase()
      var table = document.querySelector(this.dataset.tableSearch)
      var rows = table.querySelectorAll("tbody tr")

      rows.forEach((row) => {
        var text = row.textContent.toLowerCase()
        row.style.display = text.includes(filter) ? "" : "none"
      })
    })
  })

  // Canvas para firma digital
  var canvas = document.getElementById("signature-canvas")
  if (canvas) {
    var ctx = canvas.getContext("2d")
    var isDrawing = false
    var lastPoint = { x: 0, y: 0 }

    canvas.addEventListener("mousedown", function (e) {
      isDrawing = true
      lastPoint = { x: e.offsetX, y: e.offsetY }
    })
    canvas.addEventListener("mouseup", function () {
      isDrawing = false
    })
    canvas.addEventListener("mouseout", function () {
      isDrawing = false
    })
    canvas.addEventListener("mousemove", function (e) {
      if (isDrawing) {
        ctx.beginPath()
        ctx.moveTo(lastPoint.x, lastPoint.y)
        ctx.lineTo(e.offsetX, e.offsetY)
        ctx.stroke()
        lastPoint = { x: e.offsetX, y: e.offsetY }
      }
    })
    // Botón limpiar firma
    var clearBtn = document.getElementById("clear-signature")
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      })
    }
  }

  // Cálculo de tiempo (ejemplo: para servicios)
  var horaInicioInput = document.getElementById("hora_inicio")
  var horaFinInput = document.getElementById("hora_fin")
  var tiempoTotalSpan = document.getElementById("tiempo_total")

  function convertirAMinutos(tiempo) {
    var partes = tiempo.split(":")
    return Number.parseInt(partes[0]) * 60 + Number.parseInt(partes[1])
  }

  function calcularTiempo() {
    if (horaInicioInput && horaFinInput && tiempoTotalSpan) {
      var inicio = horaInicioInput.value
      var fin = horaFinInput.value
      if (inicio && fin) {
        var inicioMinutos = convertirAMinutos(inicio)
        var finMinutos = convertirAMinutos(fin)
        if (finMinutos > inicioMinutos) {
          var diferencia = finMinutos - inicioMinutos
          var horas = Math.floor(diferencia / 60)
          var minutos = diferencia % 60
          tiempoTotalSpan.textContent = horas + "h " + minutos + "m"
        }
      }
    }
  }

  if (horaInicioInput) horaInicioInput.addEventListener("input", calcularTiempo)
  if (horaFinInput) horaFinInput.addEventListener("input", calcularTiempo)
})