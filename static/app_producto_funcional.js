const app = {
    url: "",
    tablaActual: "",
    datosActuales: [],
    productoEditandoId: null,

    // ==================================================
    // CARGAR UNA TABLA DESDE FLASK
    // ==================================================
    cargarTabla: async (tabla) => {
        app.tablaActual = tabla;
        app.datosActuales = [];
        app.productoEditandoId = null;

        const container = document.getElementById("content");

        if (!container) {
            console.error("No existe el contenedor #content");
            return;
        }

        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-capitalize text-secondary">
                    ${tabla.replaceAll("_", " ")}
                </h2>

                <button
                    type="button"
                    class="btn btn-primary shadow-sm"
                    onclick="app.mostrarFormulario('${tabla}')"
                >
                    <i class="bi bi-plus-circle"></i>
                    Agregar ${tabla.replaceAll("_", " ")}
                </button>
            </div>

            <div id="modulo-formulario"></div>

            <div id="modulo-tabla"></div>
        `;

        try {
            const respuesta = await fetch(`${app.url}/${tabla}`);

            if (!respuesta.ok) {
                const texto = await respuesta.text();

                throw new Error(
                    `Error HTTP ${respuesta.status}: ${texto}`
                );
            }

            const datos = await respuesta.json();

            app.datosActuales = datos;

            app.dibujarTabla(datos);
        } catch (error) {
            console.error("Error al cargar la tabla:", error);

            const contenedorTabla =
                document.getElementById("modulo-tabla");

            if (contenedorTabla) {
                contenedorTabla.innerHTML = `
                    <div class="alert alert-danger">
                        No fue posible cargar la tabla
                        <strong>${tabla}</strong>.
                    </div>
                `;
            }
        }
    },

    // ==================================================
    // MOSTRAR FORMULARIO
    // ==================================================
    mostrarFormulario: (tabla) => {
        const contenedorFormulario =
            document.getElementById("modulo-formulario");

        if (!contenedorFormulario) {
            console.error(
                "No existe el contenedor #modulo-formulario"
            );
            return;
        }

        if (
            typeof Formularios !== "undefined" &&
            Formularios[tabla]
        ) {
            contenedorFormulario.innerHTML =
                Formularios[tabla];

            if (tabla === "producto") {
                app.productoEditandoId = null;

                const formulario =
                    document.getElementById("form_producto");

                if (formulario) {
                    const botonGuardar =
                        formulario.querySelector(
                            'button[type="submit"]'
                        );

                    if (botonGuardar) {
                        botonGuardar.innerHTML = `
                            <i class="bi bi-save"></i>
                            Guardar producto
                        `;
                    }
                }
            }
        } else {
            contenedorFormulario.innerHTML = `
                <div class="alert alert-warning">
                    El formulario para
                    <strong>${tabla}</strong>
                    todavía no está disponible.
                </div>
            `;
        }
    },

    // ==================================================
    // CANCELAR FORMULARIO
    // ==================================================
    cancelar: () => {
        app.productoEditandoId = null;

        const contenedorFormulario =
            document.getElementById("modulo-formulario");

        if (contenedorFormulario) {
            contenedorFormulario.innerHTML = "";
        }
    },

    // ==================================================
    // DIBUJAR TABLA
    // ==================================================
    dibujarTabla: (datos) => {
        const contenedorTabla =
            document.getElementById("modulo-tabla");

        if (!contenedorTabla) {
            console.error("No existe #modulo-tabla");
            return;
        }

        if (!Array.isArray(datos) || datos.length === 0) {
            contenedorTabla.innerHTML = `
                <div class="alert alert-info">
                    No hay registros en la base de datos.
                </div>
            `;
            return;
        }

        const columnas = Object.keys(datos[0]);

        const mostrarAcciones =
            app.tablaActual === "producto";

        let html = `
            <div class="table-responsive bg-white rounded border">
                <table class="table table-striped table-hover table-bordered mb-0">
                    <thead class="table-dark">
                        <tr>
        `;

        columnas.forEach((columna) => {
            html += `
                <th>${columna.toUpperCase()}</th>
            `;
        });

        if (mostrarAcciones) {
            html += `
                <th style="min-width: 200px;">
                    ACCIONES
                </th>
            `;
        }

        html += `
                        </tr>
                    </thead>

                    <tbody>
        `;

        datos.forEach((fila, indice) => {
            html += "<tr>";

            columnas.forEach((columna) => {
                let valor = fila[columna];

                if (valor === null || valor === undefined) {
                    valor = "-";
                }

                html += `<td>${valor}</td>`;
            });

            if (mostrarAcciones) {
                html += `
                    <td>
                        <button
                            type="button"
                            class="btn btn-warning btn-sm me-1"
                            onclick="app.editarRegistro(${indice})"
                        >
                            <i class="bi bi-pencil-square"></i>
                            Editar
                        </button>

                        <button
                            type="button"
                            class="btn btn-danger btn-sm"
                            onclick="app.eliminarRegistro(${fila.id_producto})"
                        >
                            <i class="bi bi-trash"></i>
                            Eliminar
                        </button>
                    </td>
                `;
            }

            html += "</tr>";
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contenedorTabla.innerHTML = html;
    },

    // ==================================================
    // CARGAR PRODUCTO EN EL FORMULARIO PARA EDITAR
    // ==================================================
    editarRegistro: (indice) => {
        if (app.tablaActual !== "producto") {
            return;
        }

        const producto = app.datosActuales[indice];

        if (!producto) {
            alert("No se encontró el producto seleccionado.");
            return;
        }

        app.mostrarFormulario("producto");

        app.productoEditandoId = producto.id_producto;

        const campos = [
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "fecha_caducidad",
            "id_categoria",
            "id_proveedor"
        ];

        campos.forEach((campo) => {
            const elemento = document.getElementById(campo);

            if (elemento) {
                elemento.value =
                    producto[campo] === null ||
                    producto[campo] === undefined
                        ? ""
                        : producto[campo];
            }
        });

        const formulario =
            document.getElementById("form_producto");

        if (formulario) {
            const botonGuardar =
                formulario.querySelector(
                    'button[type="submit"]'
                );

            if (botonGuardar) {
                botonGuardar.innerHTML = `
                    <i class="bi bi-check-circle"></i>
                    Actualizar producto
                `;
            }

            formulario.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    },

    // ==================================================
    // ELIMINAR PRODUCTO
    // ==================================================
    eliminarRegistro: async (idProducto) => {
        if (app.tablaActual !== "producto") {
            return;
        }

        const confirmar = window.confirm(
            `¿Deseas eliminar el producto con ID ${idProducto}?`
        );

        if (!confirmar) {
            return;
        }

        try {
            const respuesta = await fetch(
                `${app.url}/producto/${idProducto}`,
                {
                    method: "DELETE"
                }
            );

            const resultado =
                await app.obtenerRespuesta(respuesta);

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    "No fue posible eliminar el producto"
                );
            }

            alert(
                resultado.mensaje ||
                "Producto eliminado correctamente"
            );

            await app.cargarTabla("producto");
        } catch (error) {
            console.error("Error al eliminar:", error);

            alert(
                "No fue posible eliminar el producto.\n\n" +
                error.message
            );
        }
    },

    // ==================================================
    // GUARDAR O ACTUALIZAR
    // ==================================================
    guardar: async (evento, tabla) => {
        evento.preventDefault();

        const formulario =
            document.getElementById(`form_${tabla}`);

        if (!formulario) {
            alert(`No se encontró el formulario de ${tabla}.`);
            return;
        }

        const elementos = formulario.querySelectorAll(
            "input, textarea, select"
        );

        const datos = {};

        elementos.forEach((elemento) => {
            if (!elemento.id) {
                return;
            }

            if (elemento.type === "number") {
                datos[elemento.id] =
                    elemento.value === ""
                        ? null
                        : Number(elemento.value);
            } else {
                datos[elemento.id] = elemento.value;
            }
        });

        let metodo = "POST";
        let direccion = `${app.url}/${tabla}`;

        if (
            tabla === "producto" &&
            app.productoEditandoId !== null
        ) {
            metodo = "PUT";

            direccion =
                `${app.url}/producto/` +
                app.productoEditandoId;
        }

        try {
            const respuesta = await fetch(direccion, {
                method: metodo,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(datos)
            });

            const resultado =
                await app.obtenerRespuesta(respuesta);

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    `Error HTTP ${respuesta.status}`
                );
            }

            alert(
                resultado.mensaje ||
                (
                    metodo === "POST"
                        ? "Registro guardado correctamente"
                        : "Registro actualizado correctamente"
                )
            );

            app.productoEditandoId = null;
            app.cancelar();

            await app.cargarTabla(tabla);
        } catch (error) {
            console.error("Error al guardar:", error);

            alert(
                "No fue posible guardar los cambios.\n\n" +
                error.message
            );
        }
    },

    // ==================================================
    // LEER RESPUESTA JSON SIN PROVOCAR ERRORES
    // ==================================================
    obtenerRespuesta: async (respuesta) => {
        const texto = await respuesta.text();

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
};