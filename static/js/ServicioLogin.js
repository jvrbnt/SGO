const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const credentials = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });

        const data = await response.json();

        if (response.ok) {
            // Build the active user object so ServicioUsuario.js doesn't fail
            const activeUser = {
                name: data.name,
                lastName: data.lastName,
                email: data.email,
                entity: data.entity,
                profilePicture: "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png",
                requests: [],
                group: null,
                ip: null,
                account: null,
                project: null
            };

            // Save the user to local storage
            localStorage.setItem('activeUser', JSON.stringify(activeUser));
            window.location.href = "/SGO/static/html/ServicioUsuario.html";
        } else {
            // Incorrect credentials error from the backend
            alert(data.detail);
        }
    } catch (error) {
        console.error("Error connecting to the backend:", error);
        alert("Connection error. Make sure your FastAPI server is running.");
    }
});