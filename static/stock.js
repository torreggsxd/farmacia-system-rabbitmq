let stock = [];

function addStock() {
    const name = document.getElementById("pname").value;
    const qty = document.getElementById("pstock").value;

    stock.push({ name, qty });

    renderStock();
}

function renderStock() {
    let html = "";

    stock.forEach((p, i) => {
        html += `
        <tr>
            <td>${p.name}</td>
            <td>${p.qty}</td>
            <td><button onclick="removeStock(${i})">X</button></td>
        </tr>`;
    });

    document.getElementById("stockTable").innerHTML = html;
}

function removeStock(i) {
    stock.splice(i, 1);
    renderStock();
}