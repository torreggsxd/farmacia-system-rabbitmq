async function login() {

    const user = document.getElementById("user").value;
    const password = document.getElementById("password").value;
    const msg = document.getElementById("msg");

    msg.innerText = "Validando...";

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                correo: user,
                contrasena: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            msg.style.color = "green";
            msg.innerText = data.message + " (" + data.role + ")";
        } else {
            msg.style.color = "red";
            msg.innerText = data.message;
        }

    } catch (error) {
        msg.style.color = "red";
        msg.innerText = "Error de conexión con el servidor";
    }
}