window.addEventListener("DOMContentLoaded", async () => {
  if (window.location.pathname !== "/web/public/index.html") {
    LoopIndex();
  }
  // 1. Sincroniza todos los puntos y reviews de todos los usuarios
  try {
    const res = await fetch('/api/all_users_data');
    if (res.ok) {
      const all = await res.json();
      for (const usuario in all) {
        if (all[usuario].points)
          localStorage.setItem(`${usuario}_points`, JSON.stringify(all[usuario].points));
        if (all[usuario].reviews)
          localStorage.setItem(`${usuario}_reviews`, JSON.stringify(all[usuario].reviews));
      }
    }
  } catch (e) {
    console.error("❌ Error sincronizando usuarios:", e);
  }

  // 2. Sincroniza general_data global
  try {
    const resGen = await fetch('/api/general_data');
    if (resGen.ok) {
      const general = await resGen.json();
      localStorage.setItem("general_data", JSON.stringify(general));
    }
  } catch (e) {
    console.error("❌ Error sincronizando general_data:", e);
  }
});

function openSesion(usuario) {
  localStorage.setItem("Online", usuario);
  console.log(`Sesión abierta para ${usuario}`);
  window.location.href = "index.html";
}

function logoutUsuario() {
  if (localStorage.getItem("Online") == "") {
    console.log("No hay sesión abierta");
  }
  else {localStorage.setItem("Online", "");
    console.log("Sesión cerrada");
    window.location.href = "register.html"; // Redirigir a login
  }
}

function showLogin() {
    document.getElementById("login-form").style.display = "block";
    document.getElementById("register-form").style.display = "none";
    document.getElementById("show-login").style.backgroundColor = "yellow";
    document.getElementById("show-register").style.backgroundColor = "white";
}
function showRegister() {
    document.getElementById("login-form").style.display = "none";
    document.getElementById("register-form").style.display = "block";
        document.getElementById("show-login").style.backgroundColor = "white";
    document.getElementById("show-register").style.backgroundColor = "yellow";
}

function LoopIndex(){
  const medias = JSON.parse(localStorage.getItem("general_data") || "{}");
  for( const ciudad in medias) {
    showTotal(ciudad, medias[ciudad]);
  }
}

function showTotal(ciudad, nota){
  let variable = "id-" + ciudad;
  let elemento = document.getElementById(variable);

  if (!nota || typeof nota.total !== "number" || isNaN(nota.total)) {
    elemento.innerHTML = "NOT ENOUGH DATA";
  }

  elemento.innerHTML = nota["total"];
}

// general_data desde backend
fetch("/api/general_data")
  .then(r => r.json())
  .then(data => localStorage.setItem("general_data", JSON.stringify(data)));


fetch("/api/gepeto_reviews")
  .then(res => res.json())
  .then(data => {
    localStorage.setItem("Gepeto_reviews", JSON.stringify(data));
  });

