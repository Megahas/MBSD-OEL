function refreshData() {
    location.reload();
}

function showPopup(tableNo, status) {
    document.getElementById("popup-text").innerHTML = `
        <strong>Table No:</strong> ${tableNo}<br>
        <strong>Status:</strong> ${status}
    `;
    document.getElementById("popup-overlay").style.display = "block";
    document.getElementById("popup").style.display = "block";
}

function closePopup() {
    document.getElementById("popup-overlay").style.display = "none";
    document.getElementById("popup").style.display = "none";
}
