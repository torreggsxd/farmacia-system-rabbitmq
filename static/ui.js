renderData: (table, data, schema) => {
    const container = document.getElementById("content");
    
    if (!data || data.length === 0) {
        container.innerHTML = `
            <div class="d-flex justify-content-between mb-4">
                <h2>Tabla: ${table.toUpperCase()}</h2>
                <button class="btn btn-success" onclick="UI.showForm('${table}')">+ Nuevo</button>
            </div>
            <div class="alert alert-info">No hay registros para mostrar.</div>`;
        return;
    }

    // Obtenemos las columnas del primer objeto del JSON
    const columns = Object.keys(data[0]);

    let html = `
        <div class="d-flex justify-content-between mb-4">
            <h2 class="text-capitalize">${table}</h2>
            <button class="btn btn-success" onclick="UI.showForm('${table}')">+ Nuevo Registro</button>
        </div>
        <div id="form-container" class="card p-3 mb-3 d-none"></div>
        <table class="table table-bordered table-striped">
            <thead class="table-dark">
                <tr>${columns.map(col => `<th>${col.toUpperCase()}</th>`).join('')}<th>ACCIONES</th></tr>
            </thead>
            <tbody>
                ${data.map(row => `
                    <tr>
                        ${columns.map(col => `<td>${row[col] !== null ? row[col] : '-'}</td>`).join('')}
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="app.delete('${row[columns[0]]}')">Eliminar</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
};