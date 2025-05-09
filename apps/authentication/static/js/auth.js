function logoutUser() {
  console.log("logoutUser function called.");
  firebase
    .auth()
    .signOut()
    .then(() => {
      console.log("User signed out from Firebase.");
      firebase
        .auth()
        .setPersistence(firebase.auth.Auth.Persistence.NONE)
        .then(() => {
          console.log("Session persistence set to NONE.");
          fetch("/auth/logout/", {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
            },
          })
            .then((response) => {
              if (response.ok) {
                console.log("User logged out from Django.");
                window.location.href = "/";
              } else {
                console.error("Failed to log out from Django.");
              }
            })
            .catch((error) => {
              console.error("Error logging out from Django:", error);
            });
        })
        .catch((error) => {
          console.error("Error setting session persistence to NONE:", error);
        });
    })
    .catch((error) => {
      console.error("Error during Firebase logout:", error);
    });
}

window.addEventListener("load", function () {
  const firebaseConfig = {
    apiKey: "AIzaSyB4g5dVLxy-IwYKdoKck8Eo-J3mxcpBI_8",
    authDomain: "ferreteria-7c25b.firebaseapp.com",
    projectId: "ferreteria-7c25b",
    storageBucket: "ferreteria-7c25b.firebasestorage.app",
    messagingSenderId: "695226731429",
    appId: "1:695226731429:web:a51c1fa62b337d2413364c",
    measurementId: "G-E58ML9FRK4",
  };

  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
    console.log("Firebase initialized.");
  } else {
    console.log("Firebase already initialized.");
  }

  firebase
    .auth()
    .setPersistence(firebase.auth.Auth.Persistence.LOCAL)
    .then(() => {
      console.log("Session persistence set to LOCAL.");
    })
    .catch((error) => {
      console.error("Error setting session persistence:", error);
    });

  const uiConfig = {
    signInSuccessUrl: "/",
    signInOptions: [firebase.auth.GoogleAuthProvider.PROVIDER_ID],
    tosUrl: "/terminos-y-condiciones/",
    privacyPolicyUrl: "/politica-de-privacidad/",
    credentialHelper: firebaseui.auth.CredentialHelper.NONE,
    callbacks: {
      signInSuccessWithAuthResult: function (authResult) {
        console.log("User signed in:", authResult.user);
        authResult.user.getIdToken().then((token) => {
          console.log("Firebase token:", token); // Debugging token
          fetch("/auth/firebase-login/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ token: token }),
          })
            .then((response) => {
              console.log("Backend response status:", response.status); // Debugging response status
              if (response.ok) {
                console.log("User authenticated with Django.");
                window.location.reload(); // Reload the page to sync the state
              } else {
                response.json().then((data) => {
                  console.error("Failed to authenticate with Django:", data);
                });
              }
            })
            .catch((error) => {
              console.error("Error sending token to Django:", error);
            });
        });
        return false; // Prevent automatic redirection
      },
      uiShown: function () {
        console.log("FirebaseUI is displayed.");
      },
    },
  };

  const ui =
    firebaseui.auth.AuthUI.getInstance() ||
    new firebaseui.auth.AuthUI(firebase.auth());

  const loginModal = document.getElementById("loginModal");
  loginModal.addEventListener("shown.bs.modal", function () {
    ui.start("#firebaseui-auth-container", uiConfig);
  });

  loginModal.addEventListener("hidden.bs.modal", function () {
    document.getElementById("firebaseui-auth-container").innerHTML = "";
  });

  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      console.log("User is signed in:", user);
      console.log("User details:", {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
      });
      updateNavbarForAuthenticatedUser(user);
    } else {
      console.log("User is signed out. Attempting to reload auth state...");
      firebase
        .auth()
        .currentUser?.reload()
        .then(() => {
          const reloadedUser = firebase.auth().currentUser;
          if (reloadedUser) {
            console.log("User reloaded:", reloadedUser);
            updateNavbarForAuthenticatedUser(reloadedUser);
          } else {
            console.log("No user found after reload.");
            updateNavbarForLoggedOutUser();
          }
        })
        .catch((error) => {
          console.error("Error reloading user auth state:", error);
          updateNavbarForLoggedOutUser();
        });
    }
  });

  function updateNavbarForAuthenticatedUser(user) {
    console.log("Updating navbar for authenticated user:", user);
    const navbar = document.getElementById("navbar");
    if (navbar) {
      navbar.innerHTML = `
        <div class="dropdown">
          <button
            class="btn btn-outline-light nav-btn dropdown-toggle me-2"
            type="button"
            id="userDropdown"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="bi bi-person-circle me-2"></i> Bienvenido, ${
              user.displayName || user.email
            }
          </button>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
            <li><a class="dropdown-item" href="/auth/profile/"><i class="bi bi-person"></i> Mi Perfil</a></li>
            <li><button class="dropdown-item" onclick="logoutUser()"><i class="bi bi-box-arrow-right"></i> Cerrar Sesión</button></li>
          </ul>
        </div>
      `;
    } else {
      console.error("Navbar element not found.");
    }
  }

  function updateNavbarForLoggedOutUser() {
    console.log("Updating navbar for logged-out user.");
    const navbar = document.getElementById("navbar");
    if (navbar) {
      navbar.innerHTML = `
        <button
          class="btn btn-outline-light nav-btn"
          type="button"
          data-bs-toggle="modal"
          data-bs-target="#loginModal"
        >
          <i class="bi bi-person-circle me-2"></i> Iniciar Sesión
        </button>
      `;
    }
  }
});
