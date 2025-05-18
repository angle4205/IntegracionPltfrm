document.addEventListener("DOMContentLoaded", function () {
  // Añadir al carrito
  document.body.addEventListener("click", async function (e) {
    if (e.target.classList.contains("add-to-cart-btn")) {
      e.preventDefault();
      const btn = e.target;
      const productId = btn.dataset.productId;
      try {
        const response = await fetch(
          `/catalogo/agregar-al-carrito/${productId}/`,
          {
            method: "POST",
            headers: {
              "X-CSRFToken": getCSRFToken(),
            },
          }
        );
        const data = await response.json();
        if (data.success) {
          actualizarCarritoModal();
        } else {
          alert(data.message || "No se pudo añadir al carrito");
        }
      } catch {
        alert("Error de red");
      }
    }

    // Sumar cantidad
    if (e.target.classList.contains("btn-sumar-cantidad")) {
      const itemId = e.target.dataset.itemId;
      await modificarCantidad(itemId, 1);
    }
    // Restar cantidad
    if (e.target.classList.contains("btn-restar-cantidad")) {
      const itemId = e.target.dataset.itemId;
      await modificarCantidad(itemId, -1);
    }
    // Eliminar item
    let btnEliminar = e.target;
    if (
      btnEliminar.classList.contains("btn-eliminar-item") ||
      btnEliminar.closest(".btn-eliminar-item")
    ) {
      if (!btnEliminar.classList.contains("btn-eliminar-item")) {
        btnEliminar = btnEliminar.closest(".btn-eliminar-item");
      }
      const itemId = btnEliminar.dataset.itemId;
      await eliminarItem(itemId);
    }
  });

  // Cargar el carrito al abrir el modal
  const carritoModal = document.getElementById("carritoModal");
  if (carritoModal) {
    carritoModal.addEventListener("show.bs.modal", actualizarCarritoModal);
  }
});

// Función para actualizar el contenido del modal del carrito
async function actualizarCarritoModal() {
  try {
    const response = await fetch("/catalogo/obtener-carrito/");
    const data = await response.json();
    const contenedor = document.getElementById("carritoContenido");
    if (!contenedor) return;
    if (data.items && data.items.length > 0) {
      let html = '<ul class="list-group mb-3">';
      data.items.forEach((item) => {
        html += `
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <img src="${item.imagen}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:5px;margin-right:10px;">
              <span>${item.nombre}</span>
              <span class="text-muted small ms-2">${item.marca}</span>
            </div>
            <div class="d-flex align-items-center">
              <button class="btn btn-outline-secondary btn-sm btn-restar-cantidad" data-item-id="${item.id}">-</button>
              <span class="mx-2">${item.cantidad}</span>
              <button class="btn btn-outline-secondary btn-sm btn-sumar-cantidad" data-item-id="${item.id}">+</button>
              <button class="btn btn-outline-danger btn-sm ms-2 btn-eliminar-item" data-item-id="${item.id}">
                <i class="bi bi-trash"></i>
              </button>
            </div>
            <span class="ms-3 fw-bold">$${item.subtotal}</span>
          </li>
        `;
      });
      html += "</ul>";
      contenedor.innerHTML = html;
    } else {
      contenedor.innerHTML = `
        <div class="text-center py-5">
          <i class="bi bi-cart-x text-muted" style="font-size: 3rem"></i>
          <p class="mt-3">Tu carrito está vacío</p>
        </div>
      `;
    }
    // Actualiza totales
    document.getElementById("carritoSubtotal").textContent =
      "$" + data.subtotal;
    document.getElementById("carritoIva").textContent = "$" + data.iva;
    document.getElementById("carritoDespacho").textContent =
      "$" + data.costo_despacho;
    // Mostrar el total AJUSTADO para Stripe
    document.getElementById("carritoTotal").textContent =
      "$" + (data.total_para_stripe || data.total);

    // Mostrar ajuste Stripe si existe
    let ajusteStripeElem = document.getElementById("ajusteStripe");
    if (!ajusteStripeElem) {
      // Si no existe, lo creamos debajo del total
      const totalElem = document.getElementById("carritoTotal");
      ajusteStripeElem = document.createElement("div");
      ajusteStripeElem.id = "ajusteStripe";
      ajusteStripeElem.className = "text-warning small mt-1";
      totalElem.parentNode.appendChild(ajusteStripeElem);
    }
    if (data.ajuste_stripe && data.ajuste_stripe !== 0) {
      ajusteStripeElem.textContent = `* El monto fue ajustado en $${
        data.ajuste_stripe > 0 ? "+" : ""
      }${data.ajuste_stripe} para cumplir con los requisitos de Stripe.`;
    } else {
      ajusteStripeElem.textContent = "";
    }

    // Actualiza el botón de dirección según la selección
    const btnDireccion = document.querySelector(
      '[data-bs-target="#addressModal"]'
    );
    if (btnDireccion) {
      if (data.direccion_envio) {
        btnDireccion.innerHTML = `<i class="bi bi-geo-alt-fill me-2"></i>Dirección seleccionada: ${data.direccion_envio}`;
      } else if (data.metodo_despacho === "RETIRO_TIENDA") {
        btnDireccion.innerHTML = `<i class="bi bi-shop me-2"></i>Retiro en tienda`;
      } else {
        btnDireccion.innerHTML = `<i class="bi bi-geo-alt-fill me-2"></i>Seleccionar Dirección`;
      }
    }
  } catch {
    // Error al cargar el carrito
  }
}

async function modificarCantidad(itemId, delta) {
  // Obtén la cantidad actual del span
  const cantidadSpan = document.querySelector(
    `.btn-sumar-cantidad[data-item-id="${itemId}"]`
  ).previousElementSibling;
  let cantidadActual = parseInt(cantidadSpan.textContent);
  let nuevaCantidad = cantidadActual + delta;
  if (nuevaCantidad < 1) return;
  try {
    const response = await fetch(
      `/catalogo/actualizar-item-carrito/${itemId}/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ cantidad: nuevaCantidad }),
      }
    );
    const data = await response.json();
    if (data.success) {
      actualizarCarritoModal();
    }
  } catch {
    alert("Error al actualizar cantidad");
  }
}

async function eliminarItem(itemId) {
  if (!confirm("¿Eliminar este producto del carrito?")) return;
  try {
    const response = await fetch(`/catalogo/eliminar-del-carrito/${itemId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    });
    const data = await response.json();
    if (data.success) {
      actualizarCarritoModal();
    }
  } catch {
    alert("Error al eliminar producto");
  }
}

// CSRF helper
function getCSRFToken() {
  return (
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.querySelector('meta[name="csrf-token"]')?.content
  );
}
