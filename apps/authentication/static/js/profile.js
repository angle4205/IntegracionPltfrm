document.addEventListener("DOMContentLoaded", function () {
  // Abrir modal editar perfil
  document.getElementById("btnEditProfile").onclick = function (e) {
    e.preventDefault();
    new bootstrap.Modal(document.getElementById("editProfileModal")).show();
  };
  // Abrir modal editar foto
  document.getElementById("btnEditPhoto").onclick = function (e) {
    e.preventDefault();
    new bootstrap.Modal(document.getElementById("editPhotoModal")).show();
  };

  // Editar perfil (AJAX)
  document.getElementById("editProfileForm").onsubmit = async function (e) {
    e.preventDefault();
    const errorDiv = document.getElementById("editProfileError");
    errorDiv.style.display = "none";
    const data = {
      first_name: document.getElementById("editFirstName").value,
      last_name: document.getElementById("editLastName").value,
      email: document.getElementById("editEmail").value,
      default_address: document.getElementById("editDefaultAddress").value,
    };
    try {
      const response = await fetch("/authentication/edit-profile/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data),
      });
      const res = await response.json();
      if (response.ok) {
        window.location.reload();
      } else {
        errorDiv.textContent = res.error || "Error al guardar";
        errorDiv.style.display = "block";
      }
    } catch {
      errorDiv.textContent = "Error de red";
      errorDiv.style.display = "block";
    }
  };

  // Editar foto (AJAX)
  document.getElementById("editPhotoForm").onsubmit = async function (e) {
    e.preventDefault();
    const errorDiv = document.getElementById("editPhotoError");
    errorDiv.style.display = "none";
    const formData = new FormData(this);
    try {
      const response = await fetch("/authentication/edit-photo/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
        body: formData,
      });
      const res = await response.json();
      if (response.ok) {
        window.location.reload();
      } else {
        errorDiv.textContent = res.error || "Error al guardar";
        errorDiv.style.display = "block";
      }
    } catch {
      errorDiv.textContent = "Error de red";
      errorDiv.style.display = "block";
    }
  };

  // Vista previa de la foto
  document.getElementById("profilePictureInput").onchange = function (e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        let preview = document.getElementById("previewProfilePic");
        if (preview) {
          preview.src = ev.target.result;
        } else {
          let icon = document.getElementById("previewProfilePicIcon");
          if (icon) {
            icon.outerHTML = `<img id="previewProfilePic" src="${ev.target.result}" class="rounded-circle border mb-2" width="90" height="90" style="object-fit: cover;">`;
          }
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // CSRF helper
  function getCSRFToken() {
    return (
      document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
      document.querySelector('meta[name="csrf-token"]')?.content
    );
  }
});