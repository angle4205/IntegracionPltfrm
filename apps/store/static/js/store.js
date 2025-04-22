// Inicialización de sesión
function getCartSessionKey() {
  if (!sessionStorage.getItem("cart_session")) {
    sessionStorage.setItem("cart_session", Date.now().toString());
  }
  return sessionStorage.getItem("cart_session");
}

// Función para obtener el token CSRF
function getCSRFToken() {
  const cookieValue = document.cookie.match(
    "(^|;)\\s*csrftoken\\s*=\\s*([^;]+)"
  );
  return cookieValue ? cookieValue.pop() : "";
}

// Configuración inicial al cargar la página
document.addEventListener("DOMContentLoaded", function () {
  // Inicializar sesión
  const sessionKey = getCartSessionKey();

  // Configurar todos los botones "Añadir al carrito"
  document.querySelectorAll("[data-product-id]").forEach((button) => {
    button.addEventListener("click", function () {
      const productId = this.getAttribute("data-product-id");
      agregarAlCarrito(productId);
    });
  });

  // Cargar cantidad inicial del carrito
  actualizarContadorCarrito();
});

// Función para agregar producto al carrito
function agregarAlCarrito(productoId) {
  fetch(`/agregar-al-carrito/${productoId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "Content-Type": "application/json",
      "X-Session-Key": getCartSessionKey(),
    },
    credentials: "same-origin",
  })
    .then((response) => {
      if (!response.ok) throw new Error("Error en la respuesta del servidor");
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        mostrarNotificacion("Producto agregado al carrito", "success");
        actualizarContadorCarrito();

        // Si el modal del carrito está abierto, actualizar contenido
        if (
          document.getElementById("carritoModal").classList.contains("show")
        ) {
          cargarContenidoCarrito();
        }
      } else {
        mostrarNotificacion(
          data.message || "Error al agregar producto",
          "error"
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      mostrarNotificacion("Error de conexión con el servidor", "error");
    });
}

// Función para cargar el contenido del carrito
function cargarContenidoCarrito() {
  fetch("/obtener-carrito/", {
    headers: {
      "X-Session-Key": getCartSessionKey(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        actualizarVistaCarrito(data);
      }
    });
}

// Función para actualizar el contador del carrito
function actualizarContadorCarrito() {
  fetch("/obtener-cantidad-carrito/", {
    headers: {
      "X-Session-Key": getCartSessionKey(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const badge = document.getElementById("carritoBadge");
        if (badge) {
          badge.textContent = data.carrito_count;
          badge.style.display = data.carrito_count > 0 ? "block" : "none";
        }
      }
    });
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = "success") {
  const toastEl = document.getElementById("liveToast");
  if (toastEl) {
    const toast = new bootstrap.Toast(toastEl);
    const toastBody = toastEl.querySelector(".toast-body");

    toastBody.textContent = mensaje;
    toastEl.classList.remove("bg-success", "bg-danger");
    toastEl.classList.add(tipo === "success" ? "bg-success" : "bg-danger");

    toast.show();
  } else {
    alert(mensaje); // Fallback si no hay toast
  }
}
