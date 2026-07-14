// ==========================================================
// GENERADOR GENÉRICO DE FORMULARIOS
// Obtiene la configuración desde Flask:
// GET /configuracion-crud
// ==========================================================


// Aquí se almacenará el HTML generado para cada tabla.
// app.js continuará utilizando Formularios[tabla].
const Formularios = new Proxy({}, {

    get: (formulariosGenerados, propiedad) => {

        if (typeof propiedad !== "string") {
            return formulariosGenerados[propiedad];
        }

        if (
            Object.prototype.hasOwnProperty.call(
                formulariosGenerados,
                propiedad
            )
        ) {
            return formulariosGenerados[propiedad];
        }

        // Mientras Flask entrega la configuración,
        // se muestra una pantalla de carga.
        if (!GeneradorFormularios.configuracionCargada) {

            if (GeneradorFormularios.errorInicializacion) {
                return `
                    <div class="alert alert-danger">
                        <strong>
                            No fue posible cargar el formulario.
                        </strong>

                        <div class="mt-2">
                            ${
                                GeneradorFormularios.escaparHTML(
                                    GeneradorFormularios.errorInicializacion
                                )
                            }
                        </div>

                        <button
                            type="button"
                            class="btn btn-outline-danger btn-sm mt-3"
                            onclick="
                                GeneradorFormularios.inicializar();
                                app.mostrarFormulario('${propiedad}');
                            "
                        >
                            Intentar nuevamente
                        </button>
                    </div>
                `;
            }

            return `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <div
                            class="spinner-border spinner-border-sm me-2"
                            role="status"
                        ></div>

                        Cargando configuración del formulario...
                    </div>

                    <button
                        type="button"
                        class="btn btn-outline-primary btn-sm mt-3"
                        onclick="app.mostrarFormulario('${propiedad}')"
                    >
                        Volver a intentar
                    </button>
                </div>
            `;
        }

        return undefined;
    }
});


// ==========================================================
// MOTOR DE FORMULARIOS
// ==========================================================

const GeneradorFormularios = {

    configuracion: {},
    datosRelacionados: {},
    configuracionCargada: false,
    inicializando: false,
    errorInicializacion: null,

    // ------------------------------------------------------
    // INICIALIZACIÓN
    // ------------------------------------------------------

    inicializar: async () => {

        if (GeneradorFormularios.inicializando) {
            return;
        }

        GeneradorFormularios.inicializando = true;
        GeneradorFormularios.errorInicializacion = null;

        try {

            // Obtener la configuración central desde Flask.
            const configuracion =
                await GeneradorFormularios.obtenerJSON(
                    "/configuracion-crud"
                );

            if (
                !configuracion ||
                typeof configuracion !== "object"
            ) {
                throw new Error(
                    "Flask no devolvió una configuración válida."
                );
            }

            GeneradorFormularios.configuracion =
                configuracion;

            // Cargar registros usados por campos select.
            await GeneradorFormularios.cargarRelaciones();

            // Generar todos los formularios.
            GeneradorFormularios.generarTodos();

            GeneradorFormularios.configuracionCargada = true;

            console.log(
                "Formularios genéricos preparados:",
                Object.keys(configuracion)
            );

        } catch (error) {

            console.error(
                "Error al inicializar formularios:",
                error
            );

            GeneradorFormularios.errorInicializacion =
                error.message;

            GeneradorFormularios.configuracionCargada = false;

        } finally {

            GeneradorFormularios.inicializando = false;
        }
    },


    // ------------------------------------------------------
    // SOLICITUD HTTP
    // ------------------------------------------------------

    obtenerJSON: async (direccion) => {

        const respuesta = await fetch(direccion);

        const texto = await respuesta.text();

        let resultado = {};

        if (texto) {
            try {
                resultado = JSON.parse(texto);
            } catch {
                throw new Error(
                    `La ruta ${direccion} no devolvió JSON válido.`
                );
            }
        }

        if (!respuesta.ok) {
            throw new Error(
                resultado.error ||
                `Error HTTP ${respuesta.status} en ${direccion}`
            );
        }

        return resultado;
    },


    // ------------------------------------------------------
    // CARGAR DATOS DE LLAVES FORÁNEAS
    // ------------------------------------------------------

    cargarRelaciones: async () => {

        const tablasRelacionadas = new Set();

        Object.values(
            GeneradorFormularios.configuracion
        ).forEach((configuracionTabla) => {

            Object.values(
                configuracionTabla.campos || {}
            ).forEach((configuracionCampo) => {

                if (configuracionCampo.referencia) {

                    tablasRelacionadas.add(
                        configuracionCampo.referencia.tabla
                    );
                }
            });
        });

        const solicitudes = Array
            .from(tablasRelacionadas)
            .map(async (tablaRelacionada) => {

                try {

                    const registros =
                        await GeneradorFormularios.obtenerJSON(
                            `/${tablaRelacionada}`
                        );

                    GeneradorFormularios.datosRelacionados[
                        tablaRelacionada
                    ] = Array.isArray(registros)
                        ? registros
                        : [];

                } catch (error) {

                    console.error(
                        `No se pudo cargar la relación ${tablaRelacionada}:`,
                        error
                    );

                    GeneradorFormularios.datosRelacionados[
                        tablaRelacionada
                    ] = [];
                }
            });

        await Promise.all(solicitudes);
    },


    // ------------------------------------------------------
    // GENERAR TODOS LOS FORMULARIOS
    // ------------------------------------------------------

    generarTodos: () => {

        Object.entries(
            GeneradorFormularios.configuracion
        ).forEach(([tabla, configuracionTabla]) => {

            Formularios[tabla] =
                GeneradorFormularios.generarFormulario(
                    tabla,
                    configuracionTabla
                );
        });
    },


    // ------------------------------------------------------
    // GENERAR UN FORMULARIO
    // ------------------------------------------------------

    generarFormulario: (
        tabla,
        configuracionTabla
    ) => {

        const singular =
            configuracionTabla.singular ||
            GeneradorFormularios.formatearTexto(tabla);

        const campos =
            configuracionTabla.campos || {};

        let contenidoCampos = "";

        Object.entries(campos).forEach(
            ([nombreCampo, configuracionCampo]) => {

                contenidoCampos +=
                    GeneradorFormularios.generarCampo(
                        tabla,
                        nombreCampo,
                        configuracionCampo
                    );
            }
        );

        return `
            <div
                class="card shadow-sm border-0 mb-4"
                data-formulario-tabla="${tabla}"
            >
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">
                        <i class="bi bi-plus-circle"></i>
                        Registrar ${GeneradorFormularios.escaparHTML(
                            singular
                        )}
                    </h5>
                </div>

                <div class="card-body">

                    <form
                        id="form_${tabla}"
                        onsubmit="app.guardar(event, '${tabla}')"
                        autocomplete="off"
                    >
                        <div class="row g-3">
                            ${contenidoCampos}
                        </div>

                        <div class="mt-4 text-end">

                            <button
                                type="button"
                                class="btn btn-secondary"
                                onclick="app.cancelar()"
                            >
                                <i class="bi bi-x-circle"></i>
                                Cancelar
                            </button>

                            <button
                                type="submit"
                                class="btn btn-success"
                            >
                                <i class="bi bi-save"></i>
                                Guardar ${GeneradorFormularios.escaparHTML(
                                    singular
                                )}
                            </button>

                        </div>
                    </form>

                </div>
            </div>
        `;
    },


    // ------------------------------------------------------
    // GENERAR UN CAMPO
    // ------------------------------------------------------

    generarCampo: (
        tabla,
        nombreCampo,
        configuracionCampo
    ) => {

        const etiqueta =
            configuracionCampo.etiqueta ||
            GeneradorFormularios.formatearTexto(
                nombreCampo
            );

        const tipo =
            configuracionCampo.tipo || "text";

        const claseColumna =
            configuracionCampo.columna ||
            "col-md-6";

        const requerido =
            configuracionCampo.requerido
                ? "required"
                : "";

        const soloLectura =
            configuracionCampo.solo_lectura
                ? "readonly"
                : "";

        const maxlength =
            configuracionCampo.maxlength
                ? `maxlength="${configuracionCampo.maxlength}"`
                : "";

        const minimo =
            configuracionCampo.min !== undefined
                ? `min="${configuracionCampo.min}"`
                : "";

        const step =
            configuracionCampo.step !== undefined
                ? `step="${configuracionCampo.step}"`
                : "";

        let control = "";

        // Campo textarea
        if (tipo === "textarea") {

            control = `
                <textarea
                    class="form-control"
                    id="${nombreCampo}"
                    name="${nombreCampo}"
                    rows="2"
                    ${requerido}
                    ${soloLectura}
                    ${maxlength}
                ></textarea>
            `;

        // Campo select
        } else if (tipo === "select") {

            control =
                GeneradorFormularios.generarSelect(
                    tabla,
                    nombreCampo,
                    configuracionCampo
                );

        // Campo input
        } else {

            let eventos = "";

            // Calcular automáticamente el subtotal.
            if (
                tabla === "detalle_venta" &&
                (
                    nombreCampo === "cantidad" ||
                    nombreCampo === "precio_unitario"
                )
            ) {
                eventos += `
                    oninput="
                        GeneradorFormularios.calcularSubtotal()
                    "
                `;
            }

            control = `
                <input
                    type="${tipo}"
                    class="form-control"
                    id="${nombreCampo}"
                    name="${nombreCampo}"
                    ${requerido}
                    ${soloLectura}
                    ${maxlength}
                    ${minimo}
                    ${step}
                    ${eventos}
                >
            `;
        }

        const textoObligatorio =
            configuracionCampo.requerido
                ? `<span class="text-danger">*</span>`
                : "";

        return `
            <div class="${claseColumna}">

                <label
                    for="${nombreCampo}"
                    class="form-label"
                >
                    ${GeneradorFormularios.escaparHTML(etiqueta)}
                    ${textoObligatorio}
                </label>

                ${control}

            </div>
        `;
    },


    // ------------------------------------------------------
    // GENERAR SELECT
    // ------------------------------------------------------

    generarSelect: (
        tabla,
        nombreCampo,
        configuracionCampo
    ) => {

        let opcionesHTML = `
            <option value="">
                Seleccione una opción
            </option>
        `;

        // Select con opciones fijas.
        if (
            Array.isArray(configuracionCampo.opciones)
        ) {

            configuracionCampo.opciones.forEach(
                (opcion) => {

                    opcionesHTML += `
                        <option
                            value="${
                                GeneradorFormularios.escaparHTML(
                                    String(opcion.valor)
                                )
                            }"
                        >
                            ${
                                GeneradorFormularios.escaparHTML(
                                    String(opcion.texto)
                                )
                            }
                        </option>
                    `;
                }
            );
        }

        // Select relacionado con otra tabla.
        if (configuracionCampo.referencia) {

            const referencia =
                configuracionCampo.referencia;

            const registros =
                GeneradorFormularios.datosRelacionados[
                    referencia.tabla
                ] || [];

            registros.forEach((registro) => {

                const valor =
                    registro[referencia.valor];

                let texto =
                    registro[referencia.texto];

                if (
                    texto === null ||
                    texto === undefined ||
                    texto === ""
                ) {
                    texto = valor;
                }

                // Cuando el campo visible también es el ID,
                // se muestra como "Venta #3".
                if (
                    referencia.texto === referencia.valor
                ) {
                    texto =
                        `${GeneradorFormularios.formatearTexto(
                            referencia.tabla
                        )} #${valor}`;
                }

                opcionesHTML += `
                    <option
                        value="${
                            GeneradorFormularios.escaparHTML(
                                String(valor)
                            )
                        }"
                    >
                        ${
                            GeneradorFormularios.escaparHTML(
                                String(texto)
                            )
                        }
                    </option>
                `;
            });
        }

        let eventoCambio = "";

        // Al seleccionar un producto dentro de detalle_venta,
        // se carga su precio automáticamente.
        if (
            tabla === "detalle_venta" &&
            nombreCampo === "id_producto"
        ) {
            eventoCambio = `
                onchange="
                    GeneradorFormularios.seleccionarProducto(
                        this.value
                    )
                "
            `;
        }

        return `
            <select
                class="form-select"
                id="${nombreCampo}"
                name="${nombreCampo}"
                ${
                    configuracionCampo.requerido
                        ? "required"
                        : ""
                }
                ${eventoCambio}
            >
                ${opcionesHTML}
            </select>
        `;
    },


    // ------------------------------------------------------
    // PRECIO AUTOMÁTICO DEL PRODUCTO
    // ------------------------------------------------------

    seleccionarProducto: (idProducto) => {

        const productos =
            GeneradorFormularios.datosRelacionados
                .producto || [];

        const producto = productos.find(
            (registro) =>
                String(registro.id_producto) ===
                String(idProducto)
        );

        if (!producto) {
            return;
        }

        const campoPrecio =
            document.getElementById(
                "precio_unitario"
            );

        if (campoPrecio) {
            campoPrecio.value =
                producto.precio ?? "";

            GeneradorFormularios.calcularSubtotal();
        }
    },


    // ------------------------------------------------------
    // CALCULAR SUBTOTAL
    // ------------------------------------------------------

    calcularSubtotal: () => {

        const campoCantidad =
            document.getElementById("cantidad");

        const campoPrecio =
            document.getElementById(
                "precio_unitario"
            );

        const campoSubtotal =
            document.getElementById("subtotal");

        if (
            !campoCantidad ||
            !campoPrecio ||
            !campoSubtotal
        ) {
            return;
        }

        const cantidad =
            Number(campoCantidad.value || 0);

        const precio =
            Number(campoPrecio.value || 0);

        campoSubtotal.value =
            (cantidad * precio).toFixed(2);
    },


    // ------------------------------------------------------
    // ACTUALIZAR DATOS RELACIONADOS
    // Se usará después de crear categorías, proveedores, etc.
    // ------------------------------------------------------

    recargar: async () => {

        GeneradorFormularios.configuracionCargada = false;

        await GeneradorFormularios.cargarRelaciones();

        GeneradorFormularios.generarTodos();

        GeneradorFormularios.configuracionCargada = true;
    },


    // ------------------------------------------------------
    // FORMATEAR TEXTO
    // ------------------------------------------------------

    formatearTexto: (texto) => {

        const resultado = String(texto)
            .replaceAll("_", " ");

        return resultado.charAt(0).toUpperCase() +
            resultado.slice(1);
    },


    // ------------------------------------------------------
    // ESCAPAR HTML
    // ------------------------------------------------------

    escaparHTML: (texto) => {

        return String(texto)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }
};


// ==========================================================
// INICIAR AUTOMÁTICAMENTE AL CARGAR LA PÁGINA
// ==========================================================

GeneradorFormularios.inicializar();