# ==========================================================
# CONFIGURACIÓN CENTRAL DEL CRUD GENÉRICO
# ==========================================================

TABLAS_CRUD = {

    # ------------------------------------------------------
    # CATEGORÍA
    # ------------------------------------------------------
    "categoria": {
        "titulo": "Categorías",
        "singular": "Categoría",
        "pk": "id_categoria",
        "ocultar_lista": [],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre",
                "tipo": "text",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "descripcion": {
                "etiqueta": "Descripción",
                "tipo": "textarea",
                "requerido": False,
                "maxlength": 255,
                "columna": "col-md-6"
            }
        }
    },

    # ------------------------------------------------------
    # CLIENTE
    # ------------------------------------------------------
    "cliente": {
        "titulo": "Clientes",
        "singular": "Cliente",
        "pk": "id_cliente",
        "ocultar_lista": [],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre completo",
                "tipo": "text",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "telefono": {
                "etiqueta": "Teléfono",
                "tipo": "text",
                "requerido": False,
                "maxlength": 20,
                "columna": "col-md-6"
            },

            "direccion": {
                "etiqueta": "Dirección",
                "tipo": "text",
                "requerido": False,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "correo": {
                "etiqueta": "Correo electrónico",
                "tipo": "email",
                "requerido": False,
                "maxlength": 100,
                "columna": "col-md-6"
            }
        }
    },

    # ------------------------------------------------------
    # PRODUCTO
    # ------------------------------------------------------
    "producto": {
        "titulo": "Productos",
        "singular": "Producto",
        "pk": "id_producto",
        "ocultar_lista": [],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre del producto",
                "tipo": "text",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "descripcion": {
                "etiqueta": "Descripción",
                "tipo": "textarea",
                "requerido": False,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "precio": {
                "etiqueta": "Precio",
                "tipo": "number",
                "requerido": True,
                "step": "0.01",
                "min": 0,
                "columna": "col-md-4"
            },

            "stock": {
                "etiqueta": "Stock",
                "tipo": "number",
                "requerido": True,
                "step": "1",
                "min": 0,
                "columna": "col-md-4"
            },

            "fecha_caducidad": {
                "etiqueta": "Fecha de caducidad",
                "tipo": "date",
                "requerido": False,
                "columna": "col-md-4"
            },

            "id_categoria": {
                "etiqueta": "Categoría",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-6",

                "referencia": {
                    "tabla": "categoria",
                    "valor": "id_categoria",
                    "texto": "nombre"
                }
            },

            "id_proveedor": {
                "etiqueta": "Proveedor",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-6",

                "referencia": {
                    "tabla": "proveedor",
                    "valor": "id_proveedor",
                    "texto": "nombre"
                }
            }
        }
    },

    # ------------------------------------------------------
    # PROVEEDOR
    # ------------------------------------------------------
    "proveedor": {
        "titulo": "Proveedores",
        "singular": "Proveedor",
        "pk": "id_proveedor",
        "ocultar_lista": [],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre del proveedor",
                "tipo": "text",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "telefono": {
                "etiqueta": "Teléfono",
                "tipo": "text",
                "requerido": False,
                "maxlength": 20,
                "columna": "col-md-6"
            },

            "direccion": {
                "etiqueta": "Dirección",
                "tipo": "text",
                "requerido": False,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "correo": {
                "etiqueta": "Correo electrónico",
                "tipo": "email",
                "requerido": False,
                "maxlength": 100,
                "columna": "col-md-6"
            }
        }
    },

    # ------------------------------------------------------
    # USUARIO
    # ------------------------------------------------------
    "usuario": {
        "titulo": "Usuarios",
        "singular": "Usuario",
        "pk": "id_usuario",

        # La contraseña no se mostrará en la tabla HTML.
        "ocultar_lista": [
            "contrasena"
        ],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre",
                "tipo": "text",
                "requerido": True,
                "maxlength": 50,
                "columna": "col-md-6"
            },

            "apellido": {
                "etiqueta": "Apellido",
                "tipo": "text",
                "requerido": False,
                "maxlength": 50,
                "columna": "col-md-6"
            },

            "correo": {
                "etiqueta": "Correo electrónico",
                "tipo": "email",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "contrasena": {
                "etiqueta": "Contraseña",
                "tipo": "password",
                "requerido": True,
                "maxlength": 500,
                "columna": "col-md-6",
                "preservar_vacio_edicion": True
            },

            "rol": {
                "etiqueta": "Rol",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-6",

                "opciones": [
                    {
                        "valor": "Administrador",
                        "texto": "Administrador"
                    },
                    {
                        "valor": "Empleado",
                        "texto": "Empleado"
                    }
                ]
            }
        }
    },

    # ------------------------------------------------------
    # FALLECIDO
    # ------------------------------------------------------
    "fallecido": {
        "titulo": "Fallecidos",
        "singular": "Fallecido",
        "pk": "id_fallecido",
        "ocultar_lista": [],

        "campos": {
            "nombre": {
                "etiqueta": "Nombre",
                "tipo": "text",
                "requerido": True,
                "maxlength": 100,
                "columna": "col-md-6"
            },

            "fecha_fallecimiento": {
                "etiqueta": "Fecha de fallecimiento",
                "tipo": "date",
                "requerido": True,
                "columna": "col-md-6"
            },

            "causa_fallecimiento": {
                "etiqueta": "Causa de fallecimiento",
                "tipo": "text",
                "requerido": True,
                "maxlength": 150,
                "columna": "col-md-6"
            },

            "observaciones": {
                "etiqueta": "Observaciones",
                "tipo": "textarea",
                "requerido": False,
                "maxlength": 255,
                "columna": "col-md-6"
            }
        }
    },

    # ------------------------------------------------------
    # VENTA
    # ------------------------------------------------------
    "venta": {
        "titulo": "Ventas",
        "singular": "Venta",
        "pk": "id_venta",
        "ocultar_lista": [],
        "formulario_especial": "venta",
        "solo_lectura_crud": True,

        "campos": {
            "fecha": {
                "etiqueta": "Fecha de venta",
                "tipo": "date",
                "requerido": True,
                "columna": "col-md-4"
            },

            "total": {
                "etiqueta": "Total",
                "tipo": "number",
                "requerido": True,
                "step": "0.01",
                "min": 0,
                "columna": "col-md-4"
            },

            "id_cliente": {
                "etiqueta": "Cliente",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-4",

                "referencia": {
                    "tabla": "cliente",
                    "valor": "id_cliente",
                    "texto": "nombre"
                }
            },

            "id_usuario": {
                "etiqueta": "Empleado",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-4",

                "referencia": {
                    "tabla": "usuario",
                    "valor": "id_usuario",
                    "texto": "nombre"
                }
            }
        }
    },

    # ------------------------------------------------------
    # DETALLE DE VENTA
    # ------------------------------------------------------
    "detalle_venta": {
        "titulo": "Detalles de venta",
        "singular": "Detalle de venta",
        "pk": "id_detalle",
        "ocultar_lista": [],
        "solo_lectura_crud": True,

        "campos": {
            "cantidad": {
                "etiqueta": "Cantidad",
                "tipo": "number",
                "requerido": True,
                "step": "1",
                "min": 1,
                "columna": "col-md-4"
            },

            "precio_unitario": {
                "etiqueta": "Precio unitario",
                "tipo": "number",
                "requerido": True,
                "step": "0.01",
                "min": 0,
                "columna": "col-md-4"
            },

            "subtotal": {
                "etiqueta": "Subtotal",
                "tipo": "number",
                "requerido": False,
                "step": "0.01",
                "min": 0,
                "solo_lectura": True,
                "calculado": True,
                "columna": "col-md-4"
            },

            "id_venta": {
                "etiqueta": "Venta",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-6",

                "referencia": {
                    "tabla": "venta",
                    "valor": "id_venta",
                    "texto": "id_venta"
                }
            },

            "id_producto": {
                "etiqueta": "Producto",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-6",

                "referencia": {
                    "tabla": "producto",
                    "valor": "id_producto",
                    "texto": "nombre"
                }
            }
        }
    },

    # ------------------------------------------------------
    # FACTURA
    # ------------------------------------------------------
    "factura": {
        "titulo": "Facturas",
        "singular": "Factura",
        "pk": "id_factura",
        "ocultar_lista": [],
        "formulario_especial": "venta",
        "solo_lectura_crud": True,

        "campos": {
            "fecha_emision": {
                "etiqueta": "Fecha de emisión",
                "tipo": "date",
                "requerido": True,
                "columna": "col-md-4"
            },

            "total": {
                "etiqueta": "Total",
                "tipo": "number",
                "requerido": True,
                "step": "0.01",
                "min": 0,
                "columna": "col-md-4"
            },

            "id_venta": {
                "etiqueta": "Venta",
                "tipo": "select",
                "requerido": True,
                "columna": "col-md-4",

                "referencia": {
                    "tabla": "venta",
                    "valor": "id_venta",
                    "texto": "id_venta"
                }
            }
        }
    }
}