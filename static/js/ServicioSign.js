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
        passwordStrengthMsg.textContent = "Strength: High"; passwordStrengthMsg.style.color = "green";
    } else if (pass.length > 6) {
        passwordStrengthMsg.textContent = "Strength: Medium"; passwordStrengthMsg.style.color = "orange";
    } else {
        passwordStrengthMsg.textContent = "Strength: Low"; passwordStrengthMsg.style.color = "red";
    }
});

// Send data to the Backend (PostgreSQL) instead of localStorage
registrationForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // Basic fields expected by the database
    const newUser = {
        first_name: document.getElementById('name').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        password: passwordInput.value,
        entity: selectEntity.value,
        // Campos extra MiNa
        research_group: document.getElementById('group').value || null,
        principal_investigator: document.getElementById('ip').value || null,
        internal_account: document.getElementById('cuenta').value || null,
        project_code: document.getElementById('proyecto').value || null
    };

    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newUser)
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message); // "Account created successfully"
            window.location.href = "/static/html/ServicioLogin.html";
        } else {
            // Backend returns an error (e.g.: Email is already registered)
            alert(data.detail); 
        }
    } catch (error) {
        console.error("Error connecting to the backend:", error);
        alert("Connection error. Make sure your FastAPI server is running.");
    }
});