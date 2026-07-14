// Objeto modular que contiene la estructura HTML de cada formulario
const Formularios = {
    
    // Módulo: Productos
    producto: `
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-box-seam"></i> Registrar Nuevo Producto</h5>
            </div>
            <div class="card-body">
                <form id="form_producto" onsubmit="app.guardar(event, 'producto')">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nombre del Producto</label>
                            <input type="text" class="form-control" id="nombre" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Precio Unitario</label>
                            <input type="number" step="0.01" class="form-control" id="precio" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Stock Inicial</label>
                            <input type="number" class="form-control" id="stock" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Fecha de Caducidad</label>
                            <input type="date" class="form-control" id="fecha_caducidad">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">ID Categoría</label>
                            <input type="number" class="form-control" id="id_categoria" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">ID Proveedor</label>
                            <input type="number" class="form-control" id="id_proveedor" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Descripción</label>
                            <textarea class="form-control" id="descripcion" rows="1"></textarea>
                        </div>
                    </div>
                    <div class="mt-4 text-end">
                        <button type="button" class="btn btn-secondary" onclick="app.cancelar()">Cancelar</button>
                        <button type="submit" class="btn btn-success"><i class="bi bi-save"></i> Guardar Producto</button>
                    </div>
                </form>
            </div>
        </div>
    `,

    // Módulo: Clientes
    cliente: `
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="bi bi-people"></i> Registrar Nuevo Cliente</h5>
            </div>
            <div class="card-body">
                <form id="form_cliente" onsubmit="app.guardar(event, 'cliente')">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Nombre Completo</label>
                            <input type="text" class="form-control" id="nombre" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Teléfono</label>
                            <input type="tel" class="form-control" id="telefono">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Correo Electrónico</label>
                            <input type="email" class="form-control" id="correo">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Dirección</label>
                            <input type="text" class="form-control" id="direccion">
                        </div>
                    </div>
                    <div class="mt-4 text-end">
                        <button type="button" class="btn btn-secondary" onclick="app.cancelar()">Cancelar</button>
                        <button type="submit" class="btn btn-success"><i class="bi bi-save"></i> Guardar Cliente</button>
                    </div>
                </form>
            </div>
        </div>
    `
};