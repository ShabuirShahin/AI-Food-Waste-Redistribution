function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (username === "" || password === "") {
        alert("Please enter username and password");
        return;
    }

    // DEMO PURPOSE LOGIN
    // In real life this connects to backend
    alert("Login Successful!");

    // Redirect to main page
    window.location.href = "index.html";
}