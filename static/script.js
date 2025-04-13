window.onload = () => {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(position => {
            fetch('/get_risk_by_location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById("result").innerText = "Error: " + data.error;
                } else {
                    document.getElementById("result").innerHTML = `
                        <h3>District: ${data.district}</h3>
                        <p>Total Rape: ${data.total_rape}</p>
                        <p>Risk Rate: ${data.risk_rate}</p>
                        <p>Risk Level: ${data.risk_level}</p>
                    `;
                }
            });
        }, error => {
            document.getElementById("result").innerText = "Location permission denied.";
        });
    } else {
        document.getElementById("result").innerText = "Geolocation not supported.";
    }
}
