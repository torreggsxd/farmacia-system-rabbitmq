var app = {
    url: "",
    tablaActual: "",
    datosActuales: [],
    configuracionCrud: {},
    registroEditandoId: null,
    configuracionCargada: false,

    // ======================================================
    // CARGAR CONFIGURACIÓN DEL CRUD
    // ======================================================
    cargarConfiguracion: async () => {
        if (app.configuracionCargada) {
            return;
        }

        const respuesta = await fetch(
            `${app.url}/configuracion-crud`
        );

        const resultado =
            await app.obtenerRespuesta(respuesta);

        if (!respuesta.ok) {
            throw new Error(
                resultado.error ||
                "No fue posible cargar la configuración"
            );
        }

        app.configuracionCrud = resultado;
        app.configuracionCargada = true;
    },

    // ======================================================
    // ESPERAR A QUE LOS FORMULARIOS ESTÉN LISTOS
    // ======================================================
    asegurarFormularios: async () => {
        if (typeof GeneradorFormularios === "undefined") {
            throw new Error(
                "No se cargó static/formularios.js"
            );
        }

        if (
            !GeneradorFormularios.configuracionCargada &&
            !GeneradorFormularios.inicializando
        ) {
            await GeneradorFormularios.inicializar();
        }

        const tiempoInicio = Date.now();

        while (
            !GeneradorFormularios.configuracionCargada &&
            !GeneradorFormularios.errorInicializacion
        ) {
            if (Date.now() - tiempoInicio > 5000) {
                throw new Error(
                    "El generador de formularios tardó demasiado en iniciar"
                );
            }

            await new Promise(
                resolver => setTimeout(resolver, 100)
            );
        }

        if (GeneradorFormularios.errorInicializacion) {
            throw new Error(
                GeneradorFormularios.errorInicializacion
            );
        }
    },

    // ======================================================
    // CARGAR TABLA
    // ======================================================
    cargarTabla: async (tabla) => {
        app.tablaActual = tabla;
        app.datosActuales = [];
        app.registroEditandoId = null;

        const contenedorPrincipal =
            document.getElementById("content");

        if (!contenedorPrincipal) {
            console.error(
                "No existe el contenedor con id='content'"
            );
            return;
        }

        contenedorPrincipal.innerHTML = `
            <div class="text-center py-5">
                <div
                    class="spinner-border text-primary"
                    role="status"
                ></div>

                <p class="mt-3">
                    Cargando información...
                </p>
            </div>
        `;

        try {
            await app.cargarConfiguracion();

            const configuracion =
                app.configuracionCrud[tabla];

            if (!configuracion) {
                throw new Error(
                    `La tabla '${tabla}' no está configurada`
                );
            }

            const respuesta = await fetch(
                `${app.url}/${tabla}`
            );

            const resultado =
                await app.obtenerRespuesta(respuesta);

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    `Error HTTP ${respuesta.status}`
                );
            }

            if (!Array.isArray(resultado)) {
                throw new Error(
                    "El servidor no devolvió una lista de registros"
                );
            }

            app.datosActuales = resultado;

            const titulo =
                configuracion.titulo ||
                app.formatearTexto(tabla);

            const singular =
                configuracion.singular ||
                app.formatearTexto(tabla);

            const soloLectura =
                configuracion.solo_lectura_crud === true;

            let botonPrincipal = "";

            if (
                configuracion.formulario_especial === "venta"
            ) {
                botonPrincipal = `
                    <button
                        type="button"
                        class="btn btn-primary shadow-sm"
                        onclick="VentasUI.mostrarFormulario()"
                    >
                        <i class="bi bi-cart-plus"></i>
                        Registrar venta
                    </button>
                `;
            } else if (!soloLectura) {
                botonPrincipal = `
                    <button
                        type="button"
                        class="btn btn-primary shadow-sm"
                        onclick="app.mostrarFormulario('${tabla}', 'nuevo')"
                    >
                        <i class="bi bi-plus-circle"></i>
                        Agregar ${app.escaparHTML(singular)}
                    </button>
                `;
            }

            contenedorPrincipal.innerHTML = `
                <div
                    class="d-flex justify-content-between
                    align-items-center mb-4"
                >
                    <div>
                        <h2 class="text-secondary mb-1">
                            ${app.escaparHTML(titulo)}
                        </h2>

                        <small class="text-muted">
                            Registros encontrados:
                            ${resultado.length}
                        </small>
                    </div>

                    ${botonPrincipal}
                </div>

                <div id="modulo-formulario"></div>

                <div id="modulo-tabla"></div>
            `;

            app.dibujarTabla(resultado);

        } catch (error) {
            console.error(
                `Error al cargar ${tabla}:`,
                error
            );

            contenedorPrincipal.innerHTML = `
                <div class="alert alert-danger">
                    <h5>
                        <i class="bi bi-exclamation-triangle"></i>
                        No fue posible cargar la información
                    </h5>

                    <p class="mb-0">
                        ${app.escaparHTML(error.message)}
                    </p>
                </div>
            `;
        }
    },

    // ======================================================
    // MOSTRAR FORMULARIO
    // ======================================================
    mostrarFormulario: async (
        tabla,
        modo = "nuevo"
    ) => {
        const contenedorFormulario =
            document.getElementById("modulo-formulario");

        if (!contenedorFormulario) {
            console.error(
                "No existe #modulo-formulario"
            );
            return;
        }

        contenedorFormulario.innerHTML = `
            <div class="alert alert-info">
                <div class="d-flex align-items-center">
                    <div
                        class="spinner-border spinner-border-sm me-2"
                    ></div>

                    Preparando formulario...
                </div>
            </div>
        `;

        try {
            await app.cargarConfiguracion();
            await app.asegurarFormularios();

            if (!app.configuracionCrud[tabla]) {
                throw new Error(
                    `No existe configuración para ${tabla}`
                );
            }

            const formularioHTML =
                Formularios[tabla];

            if (!formularioHTML) {
                throw new Error(
                    `No se generó el formulario de ${tabla}`
                );
            }

            if (modo === "nuevo") {
                app.registroEditandoId = null;
            }

            contenedorFormulario.innerHTML =
                formularioHTML;

            app.configurarFormulario(tabla, modo);

            contenedorFormulario.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            console.error(
                "Error al mostrar formulario:",
                error
            );

            contenedorFormulario.innerHTML = `
                <div class="alert alert-danger">
                    ${app.escaparHTML(error.message)}
                </div>
            `;
        }
    },

    // ======================================================
    // CONFIGURAR TÍTULO Y BOTÓN DEL FORMULARIO
    // ======================================================
    configurarFormulario: (
        tabla,
        modo
    ) => {
        const configuracion =
            app.configuracionCrud[tabla];

        const singular =
            configuracion && configuracion.singular
                ? configuracion.singular
                : app.formatearTexto(tabla);

        const formulario =
            document.getElementById(
                `form_${tabla}`
            );

        if (!formulario) {
            return;
        }

        const botonGuardar =
            formulario.querySelector(
                'button[type="submit"]'
            );

        const tarjeta =
            formulario.closest(".card");

        const tituloFormulario = tarjeta
            ? tarjeta.querySelector(".card-header h5")
            : null;

        if (modo === "editar") {
            if (botonGuardar) {
                botonGuardar.innerHTML = `
                    <i class="bi bi-check-circle"></i>
                    Actualizar ${app.escaparHTML(singular)}
                `;
            }

            if (tituloFormulario) {
                tituloFormulario.innerHTML = `
                    <i class="bi bi-pencil-square"></i>
                    Editar ${app.escaparHTML(singular)}
                `;
            }
        } else {
            if (botonGuardar) {
                botonGuardar.innerHTML = `
                    <i class="bi bi-save"></i>
                    Guardar ${app.escaparHTML(singular)}
                `;
            }

            if (tituloFormulario) {
                tituloFormulario.innerHTML = `
                    <i class="bi bi-plus-circle"></i>
                    Registrar ${app.escaparHTML(singular)}
                `;
            }
        }
    },

    // ======================================================
    // CANCELAR FORMULARIO
    // ======================================================
    cancelar: () => {
        app.registroEditandoId = null;

        const contenedorFormulario =
            document.getElementById(
                "modulo-formulario"
            );

        if (contenedorFormulario) {
            contenedorFormulario.innerHTML = "";
        }
    },

    // ======================================================
    // DIBUJAR TABLA
    // ======================================================
    dibujarTabla: (datos) => {
        const contenedorTabla =
            document.getElementById(
                "modulo-tabla"
            );

        if (!contenedorTabla) {
            console.error(
                "No existe #modulo-tabla"
            );
            return;
        }

        const configuracion =
            app.configuracionCrud[
                app.tablaActual
            ];

        if (!configuracion) {
            contenedorTabla.innerHTML = `
                <div class="alert alert-danger">
                    No existe configuración para esta tabla.
                </div>
            `;
            return;
        }

        if (
            !Array.isArray(datos) ||
            datos.length === 0
        ) {
            contenedorTabla.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    No hay registros en la base de datos.
                </div>
            `;
            return;
        }

        const pk =
            configuracion.pk;

        const camposOcultos =
            configuracion.ocultar_lista || [];

        const mostrarAcciones =
            configuracion.solo_lectura_crud !== true;

        const columnas = [
            pk,

            ...Object.keys(
                configuracion.campos || {}
            ).filter(
                campo =>
                    !camposOcultos.includes(campo)
            )
        ].filter(
            columna =>
                Object.prototype.hasOwnProperty.call(
                    datos[0],
                    columna
                )
        );

        let html = `
            <div
                class="table-responsive bg-white
                rounded border shadow-sm"
            >
                <table
                    class="table table-striped table-hover
                    table-bordered align-middle mb-0"
                >
                    <thead class="table-dark">
                        <tr>
        `;

        columnas.forEach((columna) => {
            html += `
                <th>
                    ${app.obtenerEtiquetaColumna(
                        columna,
                        configuracion
                    )}
                </th>
            `;
        });

        if (mostrarAcciones) {
            html += `
                <th style="min-width: 205px;">
                    ACCIONES
                </th>
            `;
        }

        html += `
                        </tr>
                    </thead>

                    <tbody>
        `;

        datos.forEach((registro, indice) => {
            html += "<tr>";

            columnas.forEach((columna) => {
                let valor =
                    registro[columna];

                if (
                    valor === null ||
                    valor === undefined ||
                    valor === ""
                ) {
                    valor = "-";
                }

                html += `
                    <td>
                        ${app.escaparHTML(
                            String(valor)
                        )}
                    </td>
                `;
            });

            if (mostrarAcciones) {
                const idRegistro =
                    registro[pk];

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
                            onclick="app.eliminarRegistro(${idRegistro})"
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

    // ======================================================
    // EDITAR REGISTRO
    // ======================================================
    editarRegistro: async (indice) => {
        const tabla =
            app.tablaActual;

        const configuracion =
            app.configuracionCrud[tabla];

        if (!configuracion) {
            alert(
                "No existe configuración para editar este registro."
            );
            return;
        }

        const registro =
            app.datosActuales[indice];

        if (!registro) {
            alert(
                "No se encontró el registro seleccionado."
            );
            return;
        }

        app.registroEditandoId =
            registro[configuracion.pk];

        await app.mostrarFormulario(
            tabla,
            "editar"
        );

        Object.entries(
            configuracion.campos || {}
        ).forEach(
            ([
                nombreCampo,
                configuracionCampo
            ]) => {
                const elemento =
                    document.getElementById(
                        nombreCampo
                    );

                if (!elemento) {
                    return;
                }

                if (
                    configuracionCampo.tipo ===
                    "password"
                ) {
                    elemento.value = "";
                    elemento.required = false;

                    elemento.placeholder =
                        "Dejar vacío para conservar la contraseña";

                    return;
                }

                let valor =
                    registro[nombreCampo];

                if (
                    valor === null ||
                    valor === undefined
                ) {
                    valor = "";
                }

                if (
                    elemento.type === "date" &&
                    typeof valor === "string" &&
                    valor.length >= 10
                ) {
                    valor =
                        valor.substring(0, 10);
                }

                elemento.value = valor;
            }
        );

        app.configurarFormulario(
            tabla,
            "editar"
        );

        const formulario =
            document.getElementById(
                `form_${tabla}`
            );

        if (formulario) {
            formulario.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    },

    // ======================================================
    // GUARDAR O ACTUALIZAR
    // ======================================================
    guardar: async (
        evento,
        tabla
    ) => {
        evento.preventDefault();

        const configuracion =
            app.configuracionCrud[tabla];

        if (!configuracion) {
            alert(
                "No existe configuración para esta tabla."
            );
            return;
        }

        const formulario =
            document.getElementById(
                `form_${tabla}`
            );

        if (!formulario) {
            alert(
                `No se encontró el formulario de ${tabla}.`
            );
            return;
        }

        const datos = {};

        Object.entries(
            configuracion.campos || {}
        ).forEach(
            ([
                nombreCampo,
                configuracionCampo
            ]) => {
                const elemento =
                    document.getElementById(
                        nombreCampo
                    );

                if (!elemento) {
                    return;
                }

                if (
                    configuracionCampo.tipo ===
                    "number"
                ) {
                    datos[nombreCampo] =
                        elemento.value === ""
                            ? null
                            : Number(
                                elemento.value
                            );
                } else if (
                    configuracionCampo.tipo ===
                    "password"
                ) {
                    datos[nombreCampo] =
                        elemento.value;
                } else {
                    datos[nombreCampo] =
                        elemento.value.trim();
                }
            }
        );

        let metodo = "POST";

        let direccion =
            `${app.url}/${tabla}`;

        if (
            app.registroEditandoId !== null
        ) {
            metodo = "PUT";

            direccion =
                `${app.url}/${tabla}/` +
                app.registroEditandoId;
        }

        const botonGuardar =
            formulario.querySelector(
                'button[type="submit"]'
            );

        if (botonGuardar) {
            botonGuardar.disabled = true;

            botonGuardar.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm"
                ></span>
                Guardando...
            `;
        }

        try {
            const respuesta = await fetch(
                direccion,
                {
                    method: metodo,

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(datos)
                }
            );

            const resultado =
                await app.obtenerRespuesta(
                    respuesta
                );

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

            app.registroEditandoId = null;
            app.cancelar();

            await app.actualizarRelaciones();

            await app.cargarTabla(tabla);

        } catch (error) {
            console.error(
                "Error al guardar:",
                error
            );

            alert(
                "No fue posible guardar el registro.\n\n" +
                error.message
            );

            app.configurarFormulario(
                tabla,
                app.registroEditandoId !== null
                    ? "editar"
                    : "nuevo"
            );

        } finally {
            if (botonGuardar) {
                botonGuardar.disabled = false;
            }
        }
    },

    // ======================================================
    // ELIMINAR REGISTRO
    // ======================================================
    eliminarRegistro: async (
        idRegistro
    ) => {
        const tabla =
            app.tablaActual;

        const configuracion =
            app.configuracionCrud[tabla];

        if (!configuracion) {
            alert(
                "No existe configuración para eliminar este registro."
            );
            return;
        }

        const singular =
            configuracion.singular ||
            app.formatearTexto(tabla);

        const confirmar =
            window.confirm(
                `¿Seguro que deseas eliminar ${singular} ` +
                `con ID ${idRegistro}?`
            );

        if (!confirmar) {
            return;
        }

        try {
            const respuesta = await fetch(
                `${app.url}/${tabla}/${idRegistro}`,
                {
                    method: "DELETE"
                }
            );

            const resultado =
                await app.obtenerRespuesta(
                    respuesta
                );

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    "No fue posible eliminar el registro"
                );
            }

            alert(
                resultado.mensaje ||
                "Registro eliminado correctamente"
            );

            await app.actualizarRelaciones();

            await app.cargarTabla(tabla);

        } catch (error) {
            console.error(
                "Error al eliminar:",
                error
            );

            alert(
                "No fue posible eliminar el registro.\n\n" +
                error.message
            );
        }
    },

    // ======================================================
    // ACTUALIZAR SELECTS RELACIONADOS
    // ======================================================
    actualizarRelaciones: async () => {
        if (
            typeof GeneradorFormularios !==
            "undefined"
        ) {
            try {
                await GeneradorFormularios.recargar();
            } catch (error) {
                console.warn(
                    "No se actualizaron las relaciones:",
                    error
                );
            }
        }
    },

    // ======================================================
    // LEER RESPUESTA DEL BACKEND
    // ======================================================
    obtenerRespuesta: async (
        respuesta
    ) => {
        const texto =
            await respuesta.text();

        if (!texto) {
            return {};
        }

        try {
            return JSON.parse(texto);
        } catch (error) {
            return {
                error: texto
            };
        }
    },

    // ======================================================
    // ETIQUETA DE COLUMNA
    // ======================================================
    obtenerEtiquetaColumna: (
        columna,
        configuracion
    ) => {
        if (columna === configuracion.pk) {
            return "ID";
        }

        const configuracionCampo =
            configuracion.campos &&
            configuracion.campos[columna]
                ? configuracion.campos[columna]
                : null;

        if (
            configuracionCampo &&
            configuracionCampo.etiqueta
        ) {
            return app.escaparHTML(
                configuracionCampo.etiqueta
                    .toUpperCase()
            );
        }

        return app.formatearTexto(
            columna
        ).toUpperCase();
    },

    // ======================================================
    // FORMATEAR TEXTO
    // ======================================================
    formatearTexto: (texto) => {
        const resultado =
            String(texto).replace(
                /_/g,
                " "
            );

        return (
            resultado.charAt(0).toUpperCase() +
            resultado.slice(1)
        );
    },

    // ======================================================
    // PROTEGER TEXTO HTML
    // ======================================================
    escaparHTML: (texto) => {
        return String(texto)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
};