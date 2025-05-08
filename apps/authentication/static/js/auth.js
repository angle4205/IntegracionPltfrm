// Add a logout function to clear Firebase session persistence
function logoutUser() {
  firebase
    .auth()
    .signOut()
    .then(() => {
      console.log("User signed out from Firebase.");
      // Clear session persistence
      firebase
        .auth()
        .setPersistence(firebase.auth.Auth.Persistence.NONE)
        .then(() => {
          console.log("Session persistence cleared.");
          // Log out from Django
          fetch("/auth/logout/", {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"), // Include the CSRF token
            },
          })
            .then((response) => {
              if (response.ok) {
                console.log("User logged out from Django.");
                // Redirect to the home page or update the UI
                window.location.href = "/";
              } else {
                console.error("Failed to log out from Django.");
              }
            })
            .catch((error) => {
              console.error("Error logging out from Django:", error);
            });
        });
    })
    .catch((error) => {
      console.error("Error during Firebase logout:", error);
    });
}
window.addEventListener("load", function () {
  // Firebase configuration
  const firebaseConfig = {
    apiKey: "AIzaSyB4g5dVLxy-IwYKdoKck8Eo-J3mxcpBI_8",
    authDomain: "ferreteria-7c25b.firebaseapp.com",
    projectId: "ferreteria-7c25b",
    storageBucket: "ferreteria-7c25b.firebasestorage.app",
    messagingSenderId: "695226731429",
    appId: "1:695226731429:web:a51c1fa62b337d2413364c",
    measurementId: "G-E58ML9FRK4",
  };

  // Initialize Firebase
  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
  } else {
    firebase.app(); // Use the already initialized app
  }

  // Set Firebase language to Spanish
  firebase.auth().languageCode = "es";

  // Set session persistence to LOCAL
  firebase
    .auth()
    .setPersistence(firebase.auth.Auth.Persistence.LOCAL)
    .then(() => {
      console.log("Session persistence set to LOCAL.");
    })
    .catch((error) => {
      console.error("Error setting session persistence:", error);
    });

  // FirebaseUI configuration
  const uiConfig = {
    signInSuccessUrl: "/", // Redirect URL after successful login
    signInOptions: [
      firebase.auth.GoogleAuthProvider.PROVIDER_ID, // Only Google Sign-In
    ],
    tosUrl: "/terminos-y-condiciones/", // Terms of service URL
    privacyPolicyUrl: "/politica-de-privacidad/", // Privacy policy URL
    credentialHelper: firebaseui.auth.CredentialHelper.NONE, // Disable Smart Lock
    callbacks: {
      signInSuccessWithAuthResult: function (authResult) {
        console.log("User signed in:", authResult.user);
        return true; // Redirect to `signInSuccessUrl`
      },
      uiShown: function () {
        console.log("FirebaseUI is displayed.");
      },
    },
  };

  // Initialize FirebaseUI
  const ui = new firebaseui.auth.AuthUI(firebase.auth());

  // Show the FirebaseUI widget when the modal is opened
  const loginModal = document.getElementById("loginModal");
  loginModal.addEventListener("shown.bs.modal", function () {
    ui.start("#firebaseui-auth-container", uiConfig);
  });

  // Clear the FirebaseUI widget when the modal is closed
  loginModal.addEventListener("hidden.bs.modal", function () {
    document.getElementById("firebaseui-auth-container").innerHTML = "";
  });

  // Handle Firebase authentication state changes
  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      console.log(`Signed in as ${user.displayName || user.email}`);
      user.getIdToken().then(function (token) {
        // Send the token to the Django backend
        fetch("/auth/firebase-login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"), // Include the CSRF token
          },
          body: JSON.stringify({ token: token }),
        })
          .then((response) => {
            if (response.ok) {
              console.log("User authenticated with Django.");
              updateNavbarForAuthenticatedUser(user);
            } else {
              console.error("Failed to authenticate with Django.");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      });
    } else {
      console.log("User is signed out.");
      updateNavbarForLoggedOutUser();
    }
  });

  // Helper function to update the navbar for authenticated users
  function updateNavbarForAuthenticatedUser(user) {
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
              <li>
                <a class="dropdown-item" href="/auth/profile/">
                  <i class="bi bi-person"></i> Mi Perfil
                </a>
              </li>
              <li>
                <button class="dropdown-item" onclick="logoutUser()">
                  <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                </button>
              </li>
            </ul>
          </div>
        `;
    }
  }

  // Helper function to update the navbar for logged-out users
  function updateNavbarForLoggedOutUser() {
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

  // Helper function to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
