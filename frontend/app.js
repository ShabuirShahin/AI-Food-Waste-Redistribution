function login() {
    // Demo login (no auth backend)
    window.location.href = "index.html";
}

function signup() {
    alert("Demo signup successful! Please login.");
}

function postFood() {

    document.getElementById("status").innerHTML =
        "⏳ Processing...";

    fetch("http://127.0.0.1:8000/food/post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            food_name: document.getElementById("food").value,
            quantity: document.getElementById("qty").value,
            latitude: parseFloat(document.getElementById("lat").value),
            longitude: parseFloat(document.getElementById("lon").value),
            expiry_hours: parseFloat(document.getElementById("expiry").value)
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("status").innerHTML =
            "✅ Food posted & NGOs notified";
    })
    .catch(() => {
        document.getElementById("status").innerHTML =
            "❌ Server error";
    });
}