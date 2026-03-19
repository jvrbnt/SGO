const selectEntity = document.getElementById('entity');
const extraFields = document.getElementById('extraFields');
const extraInputs = extraFields.querySelectorAll('input, select');
const registrationForm = document.getElementById('registrationForm');
const passwordInput = document.getElementById('password');
const passwordStrengthMsg = document.getElementById('passwordMessage');

// Show/Hide extra fields if entity is internal
selectEntity.addEventListener('change', function() {
    if (this.value === "mina") {
        extraFields.style.display = "flex"; 
        extraInputs.forEach(input => input.required = true);
    } else {
        extraFields.style.display = "none";
        extraInputs.forEach(input => input.required = false);
    }
});

// Password strength meter
passwordInput.addEventListener('input', function() {
    const pass = this.value;
    const hasLetters = /[a-zA-Z]/.test(pass);
    const hasNumbers = /\d/.test(pass);
    if (pass.length > 9 && hasLetters && hasNumbers) {
        passwordStrengthMsg.textContent = "Strength: High"; 
        passwordStrengthMsg.style.color = "green";
    } else if (pass.length > 6) {
        passwordStrengthMsg.textContent = "Strength: Medium"; 
        passwordStrengthMsg.style.color = "orange";
    } else {
        passwordStrengthMsg.textContent = "Strength: Low"; 
        passwordStrengthMsg.style.color = "red";
    }
});

// Send data to the Backend (PostgreSQL)
registrationForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // The keys MUST match the Pydantic schema (ClientCreateWeb) exactly
    const newClient = {
        first_name: document.getElementById('name').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        password: passwordInput.value,
        entity: selectEntity.value,
        // Map the UI fields to the updated schema attribute names
        internal_account: document.getElementById('account').value || null,
        ip_address: document.getElementById('ip').value || null,
        group_name: document.getElementById('group').value || null,
        project_id: document.getElementById('project').value || null
    };

    try {
        // Updated endpoint to match the new client-specific route
        const response = await fetch('/api/client/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newClient)
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "Account created successfully");
            window.location.href = "/static/html/ServicioLogin.html";
        } else {
            // Detailed error handling to avoid [object Object]
            if (Array.isArray(data.detail)) {
                // Validation errors from FastAPI
                const errorMsg = data.detail.map(err => `${err.loc[1]}: ${err.msg}`).join('\n');
                alert("Validation Error:\n" + errorMsg);
            } else {
                // Generic error from the backend
                alert("Error: " + (data.detail || "Something went wrong"));
            }
        }
    } catch (error) {
        console.error("Error connecting to the backend:", error);
        alert("Connection error. Make sure your FastAPI server is running.");
    }
});