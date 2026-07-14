let sales = [];

function makeSale() {
    const name = document.getElementById("saleName").value;
    const qty = document.getElementById("saleQty").value;

    sales.push({ name, qty });

    renderSales();
}

function renderSales() {
    let html = "";

    sales.forEach((s, i) => {
        html += `
        <tr>
            <td>${s.name}</td>
            <td>${s.qty}</td>
        </tr>`;
    });

    document.getElementById("salesTable").innerHTML = html;
}