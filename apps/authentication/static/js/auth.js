function openRegisterModal() {
  const loginModal = document.getElementById("loginModal");
  const registerModal = new bootstrap.Modal(
    document.getElementById("registerModal")
  );

  loginModal.addEventListener("hidden.bs.modal", function () {
    registerModal.show();
  });
}

function openLoginModal() {
  const registerModal = document.getElementById("registerModal");
  const loginModal = new bootstrap.Modal(document.getElementById("loginModal"));

  registerModal.addEventListener("hidden.bs.modal", function () {
    loginModal.show();
  });

  bootstrap.Modal.getInstance(registerModal).hide();
}
