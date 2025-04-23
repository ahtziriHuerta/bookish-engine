// ========== VARIABLES ==========
let ticket = [];

// ========== ESCÁNER ==========
function abrirEscaner() {
  document.getElementById("modalEscaner").style.display = "block";

  Quagga.init({
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: document.querySelector('#scanner-container'),
      constraints: { facingMode: "environment" }
    },
    decoder: { readers: ["code_128_reader", "code_39_reader"] }
  }, err => {
    if (err) {
      console.error(err);
      alert("No se pudo iniciar el escáner.");
      return;
    }
    Quagga.start();
  });

  Quagga.onDetected(data => {
    const codigo = data.codeResult.code;
    Quagga.offDetected();
    Quagga.stop();
    cerrarEscaner();

    fetch(`/buscar_producto/${codigo}/`)
      .then(res => res.json())
      .then(producto => {
        if (!producto.error) {
          agregarProductoAlTicket(producto);
        } else {
          alert("Producto no encontrado.");
        }
      });
  });
}

function cerrarEscaner() {
  document.getElementById("modalEscaner").style.display = "none";
  Quagga.stop();
}

// ========== BÚSQUEDA MANUAL ==========
function buscarProductoManual() {
  const codigo = document.getElementById("codigoManual").value.trim();
  if (!codigo) return alert("Ingresa un código válido");

  fetch(`/buscar_producto/${codigo}/`)
    .then(res => res.json())
    .then(producto => {
      if (!producto.error) {
        agregarProductoAlTicket(producto);
        document.getElementById("codigoManual").value = "";
      } else {
        alert("Producto no encontrado.");
      }
    });
}

// ========== TICKET ==========
function agregarProductoAlTicket(producto) {
  const lista = document.getElementById("ticket-list");
  const items = lista.querySelectorAll("li");
  let encontrado = false;

  items.forEach(item => {
    if (item.dataset.name === producto.nombre) {
      let cantidadActual = parseInt(item.dataset.cantidad);
      let stockDisponible = parseInt(producto.stock);

      if (cantidadActual >= stockDisponible) {
        alert(`⚠️ Stock insuficiente para "${producto.nombre}".`);
        encontrado = true;
        return;
      }

      let nuevaCantidad = cantidadActual + 1;
      let subtotal = (nuevaCantidad * parseFloat(item.dataset.price)).toFixed(2);
      item.dataset.cantidad = nuevaCantidad;
      item.querySelector(".texto-producto").innerHTML =
        `${producto.nombre}<br><small>Cantidad: ${nuevaCantidad} | Subtotal: $${subtotal}</small>`;

      const existente = ticket.find(p => p.id == producto.id);
      if (existente) existente.qty = nuevaCantidad;

      encontrado = true;
    }
  });

  if (!encontrado) {
    if (producto.stock <= 0) {
      alert(`❌ No hay stock disponible para "${producto.nombre}".`);
      return;
    }

    const li = document.createElement("li");
    li.dataset.name = producto.nombre;
    li.dataset.price = producto.precio;
    li.dataset.cantidad = 1;
    li.dataset.id = producto.id;
    li.innerHTML = `
      <div class="texto-producto">
        ${producto.nombre}<br><small>Cantidad: 1 | Subtotal: $${parseFloat(producto.precio).toFixed(2)}</small>
      </div>
      <button class="eliminar-btn">–</button>
    `;
    li.querySelector(".eliminar-btn").addEventListener("click", () => {
      let cantidad = parseInt(li.dataset.cantidad) - 1;
      if (cantidad <= 0) {
        li.remove();
        ticket = ticket.filter(p => p.id != producto.id);
      } else {
        li.dataset.cantidad = cantidad;
        let subtotal = (cantidad * parseFloat(li.dataset.price)).toFixed(2);
        li.querySelector(".texto-producto").innerHTML =
          `${li.dataset.name}<br><small>Cantidad: ${cantidad} | Subtotal: $${subtotal}</small>`;
        const prod = ticket.find(p => p.id == producto.id);
        if (prod) prod.qty = cantidad;
      }
      actualizarTotal();
    });

    lista.appendChild(li);

    ticket.push({
      id: producto.id,
      name: producto.nombre,
      qty: 1,
      price: parseFloat(producto.precio)
    });
  }

  actualizarTotal();
}

function actualizarTotal() {
  const totalSpan = document.getElementById("total");
  let total = 0;
  document.querySelectorAll("#ticket-list li").forEach(item => {
    total += parseFloat(item.dataset.price) * parseInt(item.dataset.cantidad);
  });
  totalSpan.textContent = `$${total.toFixed(2)}`;
}

// ========== TICKET IMPRESO ==========
function generarTicketImprimible(folio = "Sin folio", fecha = "", metodoPago = "") {
  const ventana = window.open('', '_blank', 'width=400,height=600,noopener=no');
  if (!ventana || !ventana.document) {
    alert("❌ No se pudo abrir la ventana del ticket.");
    return;
  }

  let contenido = `<h2>🧾 Ticket de Compra</h2>`;
  contenido += `<p><strong>Folio:</strong> ${folio}</p>`;
  contenido += `<p><strong>Fecha:</strong> ${fecha}</p>`;
  contenido += `<p><strong>Método de pago:</strong> ${metodoPago}</p><hr><ul>`;

  let total = 0;

  ticket.forEach(item => {
    const subtotal = parseFloat(item.price) * parseInt(item.qty);
    total += subtotal;
    contenido += `<li>${item.name} x${item.qty} - $${subtotal.toFixed(2)}</li>`;
  });

  contenido += `</ul><p><strong>Total: $${total.toFixed(2)}</strong></p>`;
  contenido += `<p>Gracias por su compra</p>`;

  ventana.document.body.innerHTML = contenido;
  ventana.print();
  ventana.close();
}


// ========== ENVIAR TICKET ==========
function vistaPreviaTicket() {
  const items = ticket.map(item => ({
    id: item.id,
    qty: item.qty,
    price: item.price
  }));

  if (items.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'Ticket vacío',
      text: 'No hay productos en el ticket.',
      confirmButtonText: 'Entendido'
    });
    return;
  }

  const total = parseFloat(document.getElementById("total").textContent.replace('$', '')) || 0;
  const efectivo = parseFloat(document.getElementById("efectivo").value);
  const metodo_pago = document.getElementById("metodo-pago").value;

  if (isNaN(efectivo) || efectivo < total) {
    Swal.fire({
      icon: 'error',
      title: 'Efectivo insuficiente',
      text: 'Debes ingresar un monto igual o mayor al total de la venta para continuar.'
    });
    return;
  }

  Swal.fire({
    title: '¿Deseas finalizar la venta?',
    html: `<p>Total: <strong>$${total.toFixed(2)}</strong></p><p>Método: ${metodo_pago}</p>`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, cobrar',
    cancelButtonText: 'Cancelar'
  }).then(result => {
    if (result.isConfirmed) {
      // Enviar al backend
      fetch('/registrar_venta/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ items, total, metodo_pago })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          Swal.fire({
            icon: 'success',
            title: '✅ Venta guardada',
            html: `<strong>Folio:</strong> ${data.folio}<br><strong>Método:</strong> ${data.metodo_pago}<br><strong>Fecha:</strong> ${data.fecha}`,
            confirmButtonText: 'Aceptar'
          }).then(() => location.reload());
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Error al guardar',
            text: data.error || 'Error desconocido'
          });
        }
      })
      .catch(err => {
        console.error("Error en fetch:", err);
        Swal.fire({
          icon: 'error',
          title: 'Fallo de conexión',
          text: 'Intenta nuevamente.'
        });
      });
    }
  });
}



// ========== STOCK ==========
function descontarStockDelServidor(productoId, cantidadVendida) {
  fetch(`/actualizar_stock/${productoId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify({ cantidad: cantidadVendida })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      const productElement = document.querySelector(`.product[data-id="${productoId}"]`);
      if (productElement) {
        productElement.setAttribute("data-stock", data.nuevo_stock);
        const stockInfo = productElement.querySelector(".stock-info");
        if (data.nuevo_stock === 0) {
          stockInfo.textContent = "Agotado";
          stockInfo.classList.add("agotado");
          productElement.classList.add("sin-stock");
        } else {
          stockInfo.textContent = `Disponibles: ${data.nuevo_stock}`;
          stockInfo.classList.remove("agotado");
          productElement.classList.remove("sin-stock");
        }
      }
    }
  });
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// ========== TECLADO ==========
function insertarNumero(num) {
  const input = document.getElementById("efectivo");
  if (num === "." && input.value.includes(".")) return;
  input.value += num;
  calcularCambio();
}

function borrarTodo() {
  const input = document.getElementById("efectivo");
  input.value = "";
  calcularCambio();
}

function calcularCambio() {
  const efectivo = parseFloat(document.getElementById("efectivo").value);
  const total = parseFloat(document.getElementById("total").textContent.replace('$', ''));
  let cambio = 0;
  if (!isNaN(efectivo) && efectivo >= total) {
    cambio = (efectivo - total).toFixed(2);
  }
  document.getElementById("cambio").textContent = `$${cambio}`;
}

// ========== EVENTOS ==========
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".product").forEach(prod => {
    prod.addEventListener("click", () => {
      const nombre = prod.dataset.name;
      const precio = prod.dataset.price;
      const stock = parseInt(prod.dataset.stock);
      const id = prod.dataset.id;

      const existente = Array.from(document.querySelectorAll("#ticket-list li"))
        .find(item => item.dataset.name === nombre);

      const cantidadActual = existente ? parseInt(existente.dataset.cantidad) : 0;

      if (cantidadActual >= stock) {
        alert(`⚠️ Ya se agregaron todas las unidades disponibles de "${nombre}".`);
        return;
      }

      agregarProductoAlTicket({ nombre, precio, stock, id });
    });
  });
});
