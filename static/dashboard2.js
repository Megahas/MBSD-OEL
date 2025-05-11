function resetData() {
    fetch('/reset_status', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateTable(); // Re-fetch and show updated statuses
            } else {
                alert('Failed to reset: ' + data.error);
            }
        })
        .catch(err => {
            console.error("Reset error:", err);
            alert('Error resetting data.');
        });
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

function updateTable() {
            fetch('/get_status')
                .then(res => res.json())
                .then(data => {
                    console.log("Received data:", data);  // Debug log
                    let html = '';
                    data.forEach(seat => {
                        html += `<tr>
                            <td>${seat.id}</td>
                            <td class="${seat.status}">${seat.status}</td>
                        </tr>`;
                    });
                    document.querySelector('#seatTable tbody').innerHTML = html;
                    lastUpdate = new Date();
                    document.getElementById('lastUpdate').textContent = 
                        `(Last updated: ${lastUpdate.toLocaleTimeString()})`;
                })
                .catch(err => {
                    console.error("Fetch error:", err);
                    document.getElementById('lastUpdate').textContent = 
                        `(Error: ${err.message})`;
                });
        }

        // Refresh every 2 seconds and on page load
        setInterval(updateTable, 2000);
        updateTable();