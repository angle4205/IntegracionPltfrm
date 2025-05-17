function openRegisterModal() {
  const loginModalEl = document.getElementById("loginModal");
  const registerModalEl = document.getElementById("registerModal");

  if (loginModalEl) {
    const loginModal =
      bootstrap.Modal.getInstance(loginModalEl) ||
      new bootstrap.Modal(loginModalEl);
    loginModal.hide();
  }
  if (registerModalEl) {
    const registerModal =
      bootstrap.Modal.getInstance(registerModalEl) ||
      new bootstrap.Modal(registerModalEl);
    registerModal.show();
  }
}

function openLoginModal() {
  const carritoModalEl = document.getElementById("carritoModal");
  const loginModalEl = document.getElementById("loginModal");

  if (carritoModalEl) {
    const carritoModal =
      bootstrap.Modal.getInstance(carritoModalEl) ||
      new bootstrap.Modal(carritoModalEl);
    carritoModal.hide();
  }
  if (loginModalEl) {
    const loginModal =
      bootstrap.Modal.getInstance(loginModalEl) ||
      new bootstrap.Modal(loginModalEl);
    loginModal.show();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // LOGIN
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const username = document.getElementById("loginUsername").value;
      const password = document.getElementById("loginPassword").value;
      const errorDiv = document.getElementById("loginError");
      errorDiv.style.display = "none";
      try {
        const response = await fetch("/authentication/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (response.ok) {
          window.location.reload();
        } else {
          errorDiv.textContent = data.error || "Error al iniciar sesión";
          errorDiv.style.display = "block";
        }
      } catch (err) {
        errorDiv.textContent = "Error de red";
        errorDiv.style.display = "block";
      }
    });
  }

  // REGISTRO
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const username = document.getElementById("registerUsername").value;
      const email = document.getElementById("registerEmail").value;
      const password = document.getElementById("registerPassword").value;
      const errorDiv = document.getElementById("registerError");
      errorDiv.style.display = "none";
      try {
        const response = await fetch("/authentication/register/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ username, email, password }),
        });
        const data = await response.json();
        if (response.ok) {
          // Opcional: mostrar mensaje de éxito y abrir modal de login
          openLoginModal();
        } else {
          errorDiv.textContent = data.error || "Error al registrarse";
          errorDiv.style.display = "block";
        }
      } catch (err) {
        errorDiv.textContent = "Error de red";
        errorDiv.style.display = "block";
      }
    });
  }
});

// Utilidad para CSRF
function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.querySelector('meta[name="csrf-token"]')?.content;
}

// Función para cerrar sesión
function logoutUser() {
  fetch("/authentication/logout/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  }).then(() => window.location.reload());
}