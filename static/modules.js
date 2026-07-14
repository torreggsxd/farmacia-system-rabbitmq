const API = "http://127.0.0.1:5000/api";

let currentTable = "";
let primaryKey = "";
let editId = null;
let columns = [];


// =========================
// MAP PRIMARY KEYS
// =========================
const PK = {
    producto: "id_producto",
    cliente: "id_cliente",
    proveedor: "id_proveedor",
    categoria: "id_categoria",
    usuario: "id_usuario",
    venta: "id_venta",
    factura: "id_factura",
    detalle_venta: "id_detalle"
};


// =========================
// CARGAR TABLA
// =========================
async function load(table) {

    currentTable = table;
    primaryKey = PK[table];

    const res = await fetch(`${API}/${table}`);
    const data = await res.json();

    if (!data || data.length === 0) {
        document.getElementById("table").innerHTML = "<h3>Sin datos</h3>";
        return;
    }

    columns = Object.keys(data[0]);

    render(data);
}


// =========================
// RENDER DINÁMICO
// =========================
function render(data) {

    let html = `<h2>${currentTable.toUpperCase()}</h2>`;

    // FORM DINÁMICO
    html += `<div style="margin-bottom:15px">`;

    columns.forEach(col => {

        if (col === primaryKey) return;

        html += `
            <input id="${col}" placeholder="${col}">
        `;
    });

    html += `
        <button onclick="save()">Guardar</button>
        <button onclick="clearForm()">Limpiar</button>
    </div>`;

    // TABLA
    html += "<table border='1' cellpadding='5'>";

    html += "<tr>";
    columns.forEach(c => html += `<th>${c}</th>`);
    html += "<th>Acciones</th></tr>";

    data.forEach(row => {

        html += "<tr>";

        columns.forEach(c => {
            html += `<td>${row[c]}</td>`;
        });

        html += `
        <td>
            <button onclick='edit(${JSON.stringify(row)})'>Editar</button>
            <button onclick='del(${row[primaryKey]})'>Eliminar</button>
        </td>
        `;

        html += "</tr>";
    });

    html += "</table>";

    document.getElementById("table").innerHTML = html;
}


// =========================
// GUARDAR (CREATE / UPDATE)
// =========================
async function save() {

    let payload = {};

    columns.forEach(col => {

        if (col === primaryKey) return;

        payload[col] = document.getElementById(col).value;
    });

    if (!editId) {

        await fetch(`${API}/${currentTable}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

    } else {

        await fetch(`${API}/${currentTable}/${editId}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        editId = null;
    }

    load(currentTable);
    clearForm();
}


// =========================
// EDITAR
// =========================
function edit(row) {

    editId = row[primaryKey];

    columns.forEach(col => {

        if (col === primaryKey) return;

        document.getElementById(col).value = row[col];
    });
}


// =========================
// ELIMINAR
// =========================
async function del(id) {

    if (!confirm("¿Eliminar registro?")) return;

    await fetch(`${API}/${currentTable}/${id}`, {
        method: "DELETE"
    });

    load(currentTable);
}


// =========================
// LIMPIAR FORM
// =========================
function clearForm() {

    editId = null;

    columns.forEach(col => {

        if (col === primaryKey) return;

        const el = document.getElementById(col);
        if (el) el.value = "";
    });
}