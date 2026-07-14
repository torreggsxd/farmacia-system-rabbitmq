let currentUser = null;

function login() {
    const user = document.getElementById("user").value;
    const pass = document.getElementById("pass").value;

    if (user === "admin" && pass === "1234") {
        currentUser = { role: "admin" };
        document.getElementById("loginView").style.display = "none";
        document.getElementById("appView").style.display = "block";
    } else {
        alert("Credenciales incorrectas");
    }
}

function logout() {
    currentUser = null;
    location.reload();
}