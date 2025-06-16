let usuarioActual = localStorage.getItem("Online"); // Se asigna en login/registro

// ✅ Función para mostrar errores visibles en pantalla
function mostrarError(mensaje) {
    // Si ya existe, solo actualiza el contenido y muestra
    let modal = document.getElementById("modal-error");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "modal-error";
        modal.innerHTML = `
            <div id="modal-error-bg" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;
                z-index: 9999;">
                <div style="
                    background: white; padding: 20px; border-radius: 8px; max-width: 400px;
                    font-family: sans-serif; box-shadow: 0 0 10px #000;">
                    <h3 style="color: #b00; margin-top: 0;">⚠️ Error</h3>
                    <p id="modal-error-msg" style="margin: 0 0 10px;"></p>
                    <button onclick="cerrarError()" style="
                        background: #b00; color: white; border: none; padding: 8px 12px; border-radius: 4px;
                        cursor: pointer;">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById("modal-error-msg").innerText = mensaje;
    document.getElementById("modal-error-bg").style.display = "flex";
    console.error("❌ " + mensaje);
}

function cerrarError() {
    const modalBg = document.getElementById("modal-error-bg");
    if (modalBg) modalBg.style.display = "none";
}


window.onload = function() {
    if (!usuarioActual || usuarioActual === "") {
        document.getElementById("login-button").style.display = "block";
        document.getElementById("logout-button").style.display = "none";
    } else {
        document.getElementById("login-button").style.display = "none";
        document.getElementById("logout-button").style.display = "block";
    }
    document.getElementById("usr").innerHTML = usuarioActual || "";
    if (window.location.pathname === "/register.html") {
        showLogin();
    }
};

async function guardarEnServidor() {
    if (!usuarioActual) {
        mostrarError("Usuario no definido. Redirigiendo a login.");
        window.location.href = "register.html";
        return;
    }

    const points = localStorage.getItem(`${usuarioActual}_points`);
    const reviews = localStorage.getItem(`${usuarioActual}_reviews`);

    if (!points || !reviews) {
        mostrarError("Faltan datos en localStorage");
        return;
    }

    const body = {
        points: JSON.parse(points),
        reviews: JSON.parse(reviews)
    };

    try {
        const res = await fetch(`/save/${usuarioActual}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const msg = await res.text();
        console.log(msg);
    } catch (e) {
        mostrarError("Error al guardar en el servidor.");
    }
}

async function cargarDesdeServidor() {
    if (!usuarioActual) {
        mostrarError("Usuario no definido. Redirigiendo a login.");
        window.location.href = "register.html";
        return;
    }

    try {
        const res = await fetch(`/load/${usuarioActual}`);
        if (!res.ok) {
            mostrarError("No se pudo cargar del servidor.");
            return;
        }

        const data = await res.json();
        localStorage.setItem(`${usuarioActual}_points`, JSON.stringify(data.points));
        localStorage.setItem(`${usuarioActual}_reviews`, JSON.stringify(data.reviews));

        console.log(`Datos cargados en localStorage para ${usuarioActual}`);
    } catch (e) {
        mostrarError("Error al conectar con el servidor.");
    }
}

function subirDesdeArchivos(files) {
    if (!usuarioActual) {
        mostrarError("Usuario no definido. Redirigiendo a login.");
        window.location.href = "register.html";
        return;
    }
    if (files.length < 2) {
        mostrarError("Selecciona los 2 archivos JSON (points y reviews).");
        return;
    }

    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const data = JSON.parse(reader.result);
                if (file.name.includes('points')) {
                    localStorage.setItem(`${usuarioActual}_points`, JSON.stringify(data));
                    console.log('Cargado points desde archivo');
                } else if (file.name.includes('reviews')) {
                    localStorage.setItem(`${usuarioActual}_reviews`, JSON.stringify(data));
                    console.log('Cargado reviews desde archivo');
                }
            } catch (e) {
                mostrarError(`Archivo mal formado: ${file.name}`);
            }
        };
        reader.readAsText(file);
    });
}

async function registrarUsuario(profile) {
    try {
        const res = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profile)
        });

        const msg = await res.text();
        console.log(msg);

        if (res.ok) {
            openSesion(profile.username);
        } else {
            mostrarError(msg);
        }
    } catch (e) {
        mostrarError("Error de red al registrar usuario.");
    }
}

async function loginUsuario(profile) {
    const { username, password } = profile;
    console.log(username, password);

    const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const text = await res.text();

    let data = {};
    try {
        data = JSON.parse(text);
    } catch (e) {
        mostrarError(`Respuesta inesperada del servidor: ${text}`);
        return false;
    }

    if (data.success) {
        usuarioActual = data.username;
        console.log(`Usuario ${usuarioActual} autenticado correctamente`);
        localStorage.setItem("Online", usuarioActual);
        openSesion(usuarioActual);
        console.log(`Login correcto: ${usuarioActual}`);
        return true;
    } else {
        mostrarError("Login fallido: " + data.message);
        return false;
    }
}



document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const userInput = document.getElementById("username");
      const passInput = document.getElementById("password");

      if (!userInput || !passInput) {
        mostrarError("No se encuentran los campos del formulario.");
        return;
      }

      const username = userInput.value
      const password = passInput.value;

      await loginUsuario({ username, password });
    });
  }
});



document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const profile = {
        username: document.getElementById("new-username").value,
        password: document.getElementById("new-password").value,
        email: document.getElementById("new-email").value,
        ciudad: document.getElementById("new-city").value
    };
    await registrarUsuario(profile);
});
