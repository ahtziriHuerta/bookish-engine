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
      } else {
        li.dataset.cantidad = cantidad;
        let subtotal = (cantidad * parseFloat(li.dataset.price)).toFixed(2);
        li.querySelector(".texto-producto").innerHTML =
          `${li.dataset.name}<br><small>Cantidad: ${cantidad} | Subtotal: $${subtotal}</small>`;
      }
      actualizarTotal();
    });

    lista.appendChild(li);
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
    alert("❌ No se pudo abrir la ventana del ticket. Desactiva el bloqueador de ventanas emergentes.");
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


function vistaPreviaTicket() {
  const efectivoInput = document.getElementById("efectivo").value;
  const totalTexto = document.getElementById("total").textContent.replace("$", "");
  const total = parseFloat(totalTexto);
  const efectivo = parseFloat(efectivoInput);
  const metodoPago = document.getElementById("metodo-pago").value || "efectivo";

  if (isNaN(efectivo) || efectivo < total) {
    alert("❌ El efectivo recibido no es suficiente para cubrir el total de la venta.");
    return;
  }

  ticket = [];
  document.querySelectorAll("#ticket-list li").forEach(item => {
    const id = item.dataset.id;
    const qty = item.dataset.cantidad;
    const name = item.dataset.name;
    const price = item.dataset.price;
    ticket.push({ id, qty, name, price });
  });

  // 🔸 Descontar stock
  ticket.forEach(item => {
    descontarStockDelServidor(item.id, item.qty);
  });

  // 🔸 Registrar venta
  fetch('/registrar_venta/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      total: total,
      items: ticket,
      metodo_pago: metodoPago
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("✅ Venta registrada con folio:", data.folio);
      generarTicketImprimible(data.folio, data.fecha, data.metodo_pago);
    } else {
      alert("❌ Error al registrar la venta: " + data.error);
    }

    // 🔸 Limpieza visual
    document.getElementById("ticket-list").innerHTML = "";
    document.getElementById("total").textContent = "$0.00";
    document.getElementById("efectivo").value = "";
    document.getElementById("cambio").textContent = "$0.00";
  })
  .catch(err => {
    alert("❌ Fallo de conexión al registrar venta: " + err.message);
  });
}

// 👇 Coloca aquí el resto de tus funciones como escáner, búsqueda, stock, teclado, etc...




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
      } else {
        alert("❌ Error al actualizar el stock: " + data.error);
      }
    })
    .catch(async (error) => {
      const text = await error.text?.();
      alert("❌ Falló la conexión al servidor: " + error.message + (text ? `\n\n${text}` : ""));
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

// ========== TECLADO NUMÉRICO ==========
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

// ========== CLIC EN PRODUCTOS ==========
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


