(() => {
    const estado = {
        clientes: [],
        productos: [],
        carrito: []
    };

    function escaparHTML(texto) {
        if (
            window.app &&
            typeof window.app.escaparHTML ===
                "function"
        ) {
            return window.app.escaparHTML(
                texto
            );
        }

        return String(texto)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function obtenerUsuarioSesion() {
        const usuarioTexto =
            localStorage.getItem("usuario");

        if (!usuarioTexto) {
            return null;
        }

        try {
            const usuario =
                JSON.parse(usuarioTexto);

            if (
                !usuario ||
                !usuario.id ||
                !usuario.nombre
            ) {
                return null;
            }

            return usuario;

        } catch (error) {
            console.error(
                "No fue posible leer el usuario:",
                error
            );

            return null;
        }
    }

    function obtenerFechaActual() {
        const fecha = new Date();

        const anio =
            fecha.getFullYear();

        const mes =
            String(
                fecha.getMonth() + 1
            ).padStart(2, "0");

        const dia =
            String(
                fecha.getDate()
            ).padStart(2, "0");

        return `${anio}-${mes}-${dia}`;
    }

    function generarOperacionId() {
        if (
            window.crypto &&
            typeof window.crypto.randomUUID ===
                "function"
        ) {
            return window.crypto.randomUUID();
        }

        return (
            Date.now().toString(16) +
            "-" +
            Math.random()
                .toString(16)
                .substring(2)
        ).substring(0, 36);
    }

    async function leerRespuesta(
        respuesta
    ) {
        const texto =
            await respuesta.text();

        if (!texto) {
            return {};
        }

        try {
            return JSON.parse(texto);

        } catch {
            return {
                error: texto
            };
        }
    }

    async function cargarLista(ruta) {
        const respuesta =
            await fetch(ruta);

        const resultado =
            await leerRespuesta(
                respuesta
            );

        if (!respuesta.ok) {
            throw new Error(
                resultado.error ||
                resultado.message ||
                `Error HTTP ${respuesta.status}`
            );
        }

        if (!Array.isArray(resultado)) {
            throw new Error(
                `La ruta ${ruta} no devolvió una lista`
            );
        }

        return resultado;
    }

    function obtenerProducto(
        idProducto
    ) {
        return estado.productos.find(
            producto =>
                Number(
                    producto.id_producto
                ) === Number(idProducto)
        );
    }

    function calcularTotal() {
        return estado.carrito.reduce(
            (total, elemento) => {
                return (
                    total +
                    Number(
                        elemento.subtotal
                    )
                );
            },
            0
        );
    }

    function generarOpcionesClientes() {
        if (estado.clientes.length === 0) {
            return `
                <option value="">
                    No hay clientes registrados
                </option>
            `;
        }

        return `
            <option value="">
                Selecciona un cliente
            </option>

            ${estado.clientes
                .map(cliente => `
                    <option
                        value="${
                            cliente.id_cliente
                        }"
                    >
                        ${escaparHTML(
                            cliente.nombre
                        )}
                    </option>
                `)
                .join("")}
        `;
    }

    function generarOpcionesProductos() {
        const productosDisponibles =
            estado.productos.filter(
                producto =>
                    Number(
                        producto.stock || 0
                    ) > 0
            );

        if (
            productosDisponibles.length === 0
        ) {
            return `
                <option value="">
                    No hay productos con stock
                </option>
            `;
        }

        return `
            <option value="">
                Selecciona un producto
            </option>

            ${productosDisponibles
                .map(producto => `
                    <option
                        value="${
                            producto.id_producto
                        }"
                    >
                        ${escaparHTML(
                            producto.nombre
                        )}
                        - $${Number(
                            producto.precio || 0
                        ).toFixed(2)}
                        - Stock:
                        ${Number(
                            producto.stock || 0
                        )}
                    </option>
                `)
                .join("")}
        `;
    }

    function construirFormulario() {
        const usuario =
            obtenerUsuarioSesion();

        if (!usuario) {
            localStorage.removeItem(
                "token"
            );

            localStorage.removeItem(
                "usuario"
            );

            window.location.replace(
                "/login"
            );

            return "";
        }

        return `
            <div
                class="card border-0
                shadow-sm mb-4"
            >
                <div
                    class="card-header
                    bg-primary text-white"
                >
                    <h5 class="mb-0">
                        <i
                            class="bi
                            bi-cart-plus"
                        ></i>
                        Registrar venta
                    </h5>
                </div>

                <div class="card-body">
                    <form id="form-venta">

                        <div class="row g-3">

                            <div class="col-md-4">
                                <label
                                    for="venta-fecha"
                                    class="form-label"
                                >
                                    Fecha
                                </label>

                                <input
                                    type="date"
                                    id="venta-fecha"
                                    class="form-control"
                                    value="${
                                        obtenerFechaActual()
                                    }"
                                    required
                                >
                            </div>

                            <div class="col-md-4">
                                <label
                                    for="venta-cliente"
                                    class="form-label"
                                >
                                    Cliente
                                </label>

                                <select
                                    id="venta-cliente"
                                    class="form-select"
                                    required
                                >
                                    ${
                                        generarOpcionesClientes()
                                    }
                                </select>
                            </div>

                            <div class="col-md-4">
                                <label
                                    for="venta-empleado"
                                    class="form-label"
                                >
                                    Empleado
                                </label>

                                <input
                                    type="text"
                                    id="venta-empleado"
                                    class="form-control"
                                    value="${escaparHTML(
                                        usuario.nombre
                                    )}"
                                    readonly
                                >

                                <div class="form-text">
                                    Trabajador autenticado
                                </div>
                            </div>

                        </div>

                        <hr class="my-4">

                        <div class="row g-3">

                            <div class="col-md-7">
                                <label
                                    for="venta-producto"
                                    class="form-label"
                                >
                                    Producto
                                </label>

                                <select
                                    id="venta-producto"
                                    class="form-select"
                                >
                                    ${
                                        generarOpcionesProductos()
                                    }
                                </select>
                            </div>

                            <div class="col-md-2">
                                <label
                                    for="venta-cantidad"
                                    class="form-label"
                                >
                                    Cantidad
                                </label>

                                <input
                                    type="number"
                                    id="venta-cantidad"
                                    class="form-control"
                                    min="1"
                                    step="1"
                                    value="1"
                                >
                            </div>

                            <div
                                class="col-md-3
                                d-flex
                                align-items-end"
                            >
                                <button
                                    type="button"
                                    class="btn
                                    btn-outline-primary
                                    w-100"
                                    onclick="
                                        VentasUI.agregarProducto()
                                    "
                                >
                                    <i
                                        class="bi
                                        bi-plus-circle"
                                    ></i>
                                    Agregar
                                </button>
                            </div>

                        </div>

                        <div
                            id="venta-carrito"
                            class="mt-4"
                        ></div>

                        <div
                            id="venta-mensaje"
                            class="mt-3"
                        ></div>

                        <div
                            class="d-flex
                            justify-content-end
                            gap-2 mt-4"
                        >
                            <button
                                type="button"
                                class="btn
                                btn-secondary"
                                onclick="
                                    VentasUI.cancelar()
                                "
                            >
                                Cancelar
                            </button>

                            <button
                                type="submit"
                                id="btn-guardar-venta"
                                class="btn
                                btn-success"
                            >
                                <i
                                    class="bi
                                    bi-check-circle"
                                ></i>
                                Registrar venta
                            </button>
                        </div>

                    </form>
                </div>
            </div>
        `;
    }

    function renderizarCarrito() {
        const contenedor =
            document.getElementById(
                "venta-carrito"
            );

        if (!contenedor) {
            return;
        }

        if (estado.carrito.length === 0) {
            contenedor.innerHTML = `
                <div class="alert alert-info">
                    <i
                        class="bi
                        bi-info-circle"
                    ></i>
                    Agrega por lo menos un producto.
                </div>
            `;

            return;
        }

        let filas = "";

        estado.carrito.forEach(
            (elemento, indice) => {
                filas += `
                    <tr>
                        <td>
                            ${escaparHTML(
                                elemento.nombre
                            )}
                        </td>

                        <td>
                            ${elemento.cantidad}
                        </td>

                        <td>
                            $${Number(
                                elemento.precio
                            ).toFixed(2)}
                        </td>

                        <td>
                            $${Number(
                                elemento.subtotal
                            ).toFixed(2)}
                        </td>

                        <td>
                            <button
                                type="button"
                                class="btn
                                btn-danger
                                btn-sm"
                                onclick="
                                    VentasUI.eliminarProducto(
                                        ${indice}
                                    )
                                "
                            >
                                <i
                                    class="bi
                                    bi-trash"
                                ></i>
                            </button>
                        </td>
                    </tr>
                `;
            }
        );

        contenedor.innerHTML = `
            <div class="table-responsive">
                <table
                    class="table
                    table-bordered
                    align-middle"
                >
                    <thead class="table-dark">
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>Subtotal</th>
                            <th>Acción</th>
                        </tr>
                    </thead>

                    <tbody>
                        ${filas}
                    </tbody>

                    <tfoot>
                        <tr>
                            <th
                                colspan="3"
                                class="text-end"
                            >
                                Total
                            </th>

                            <th colspan="2">
                                $${calcularTotal()
                                    .toFixed(2)}
                            </th>
                        </tr>
                    </tfoot>
                </table>
            </div>
        `;
    }

    async function mostrarFormulario() {
        const contenedor =
            document.getElementById(
                "modulo-formulario"
            );

        if (!contenedor) {
            alert(
                "Primero abre el módulo Venta."
            );

            return;
        }

        const usuario =
            obtenerUsuarioSesion();

        if (!usuario) {
            window.location.replace(
                "/login"
            );

            return;
        }

        contenedor.innerHTML = `
            <div class="alert alert-info">
                <span
                    class="spinner-border
                    spinner-border-sm"
                ></span>
                Preparando formulario de venta...
            </div>
        `;

        try {
            const resultados =
                await Promise.all([
                    cargarLista("/cliente"),
                    cargarLista("/producto")
                ]);

            estado.clientes =
                resultados[0];

            estado.productos =
                resultados[1];

            estado.carrito = [];

            contenedor.innerHTML =
                construirFormulario();

            renderizarCarrito();

            const formulario =
                document.getElementById(
                    "form-venta"
                );

            formulario.addEventListener(
                "submit",
                guardarVenta
            );

            contenedor.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            console.error(
                "Error al preparar venta:",
                error
            );

            contenedor.innerHTML = `
                <div class="alert alert-danger">
                    <strong>
                        No fue posible preparar la venta.
                    </strong>

                    <div>
                        ${escaparHTML(
                            error.message
                        )}
                    </div>
                </div>
            `;
        }
    }

    function agregarProducto() {
        const selector =
            document.getElementById(
                "venta-producto"
            );

        const campoCantidad =
            document.getElementById(
                "venta-cantidad"
            );

        if (
            !selector ||
            !campoCantidad
        ) {
            return;
        }

        const idProducto =
            Number(selector.value);

        const cantidad =
            Number(campoCantidad.value);

        if (!idProducto) {
            alert(
                "Selecciona un producto."
            );

            return;
        }

        if (
            !Number.isInteger(cantidad) ||
            cantidad <= 0
        ) {
            alert(
                "La cantidad debe ser un número " +
                "entero mayor que cero."
            );

            return;
        }

        const producto =
            obtenerProducto(
                idProducto
            );

        if (!producto) {
            alert(
                "No se encontró el producto."
            );

            return;
        }

        const stock =
            Number(producto.stock || 0);

        const existente =
            estado.carrito.find(
                elemento =>
                    Number(
                        elemento.id_producto
                    ) === idProducto
            );

        const cantidadActual =
            existente
                ? existente.cantidad
                : 0;

        const cantidadNueva =
            cantidadActual + cantidad;

        if (cantidadNueva > stock) {
            alert(
                `Stock insuficiente. Disponible: ${stock}`
            );

            return;
        }

        const precio =
            Number(producto.precio || 0);

        if (existente) {
            existente.cantidad =
                cantidadNueva;

            existente.subtotal =
                precio * cantidadNueva;

        } else {
            estado.carrito.push({
                id_producto:
                    producto.id_producto,

                nombre:
                    producto.nombre,

                precio,

                cantidad,

                subtotal:
                    precio * cantidad
            });
        }

        campoCantidad.value = "1";

        renderizarCarrito();
    }

    function eliminarProducto(indice) {
        estado.carrito.splice(
            indice,
            1
        );

        renderizarCarrito();
    }

    async function guardarVenta(evento) {
        evento.preventDefault();

        const usuario =
            obtenerUsuarioSesion();

        if (!usuario) {
            window.location.replace(
                "/login"
            );

            return;
        }

        const fecha =
            document
                .getElementById(
                    "venta-fecha"
                )
                .value;

        const idCliente =
            Number(
                document
                    .getElementById(
                        "venta-cliente"
                    )
                    .value
            );

        if (!fecha) {
            alert(
                "Selecciona la fecha."
            );

            return;
        }

        if (!idCliente) {
            alert(
                "Selecciona un cliente."
            );

            return;
        }

        if (estado.carrito.length === 0) {
            alert(
                "Agrega por lo menos un producto."
            );

            return;
        }

        const boton =
            document.getElementById(
                "btn-guardar-venta"
            );

        const mensaje =
            document.getElementById(
                "venta-mensaje"
            );

        boton.disabled = true;

        boton.innerHTML = `
            <span
                class="spinner-border
                spinner-border-sm"
            ></span>
            Procesando...
        `;

        mensaje.innerHTML = "";

        const datosVenta = {
            operacion_id:
                generarOperacionId(),

            fecha,

            id_cliente:
                idCliente,

            productos:
                estado.carrito.map(
                    elemento => ({
                        id_producto:
                            elemento.id_producto,

                        cantidad:
                            elemento.cantidad
                    })
                )
        };

        /*
         * No se envía id_usuario.
         *
         * Flask obtiene el empleado directamente
         * desde el JWT del usuario autenticado.
         */
        try {
            const respuesta =
                await fetch(
                    "/registrar-venta",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                datosVenta
                            )
                    }
                );

            const resultado =
                await leerRespuesta(
                    respuesta
                );

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    resultado.message ||
                    `Error HTTP ${
                        respuesta.status
                    }`
                );
            }

            if (
                respuesta.status === 202 ||
                resultado.estado ===
                    "PENDIENTE"
            ) {
                estado.carrito = [];

                renderizarCarrito();

                mensaje.innerHTML = `
                    <div
                        class="alert
                        alert-warning"
                    >
                        <i
                            class="bi
                            bi-hourglass-split"
                        ></i>

                        ${escaparHTML(
                            resultado.mensaje ||
                            (
                                "La venta quedó " +
                                "pendiente en RabbitMQ."
                            )
                        )}
                    </div>
                `;

                return;
            }

            alert(
                resultado.mensaje ||
                "Venta registrada correctamente"
            );

            estado.carrito = [];

            if (
                window.app &&
                typeof window.app.cargarTabla ===
                    "function"
            ) {
                await window.app.cargarTabla(
                    "venta"
                );
            }

        } catch (error) {
            console.error(
                "Error al registrar venta:",
                error
            );

            mensaje.innerHTML = `
                <div class="alert alert-danger">
                    <i
                        class="bi
                        bi-exclamation-triangle"
                    ></i>

                    ${escaparHTML(
                        error.message
                    )}
                </div>
            `;

        } finally {
            boton.disabled = false;

            boton.innerHTML = `
                <i
                    class="bi
                    bi-check-circle"
                ></i>
                Registrar venta
            `;
        }
    }

    function cancelar() {
        estado.carrito = [];

        const contenedor =
            document.getElementById(
                "modulo-formulario"
            );

        if (contenedor) {
            contenedor.innerHTML = "";
        }
    }

    window.VentasUI = {
        mostrarFormulario,
        agregarProducto,
        eliminarProducto,
        cancelar
    };
})();