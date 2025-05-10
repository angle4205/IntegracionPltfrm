function openRegisterModal() {
  const loginModal = bootstrap.Modal.getInstance(
    document.getElementById("loginModal")
  );
  const registerModal = new bootstrap.Modal(
    document.getElementById("registerModal")
  );

  loginModal.hide();
  registerModal.show();
}

function openLoginModal() {
  const carritoModal = bootstrap.Modal.getInstance(
    document.getElementById("carritoModal")
  );
  const loginModal = new bootstrap.Modal(document.getElementById("loginModal"));

  if (carritoModal) {
    carritoModal.hide();
  }

  loginModal.show();
}
