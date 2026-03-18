document.addEventListener("DOMContentLoaded", () => {
    const activeUser = JSON.parse(localStorage.getItem('activeUser'));
    
    // 1. Security redirect
    if (!activeUser) {
        window.location.href = "/SGO/static/html/ServicioLogin.html";
        return;
    }

    // 2. Name + Last Name or Nickname logic
    let displayName = "";
    if (activeUser.nickname && activeUser.nickname.trim() !== "") {
        displayName = activeUser.nickname;
    } else {
        // Combine name and lastName if they exist
        const fullName = `${activeUser.name || ""} ${activeUser.lastName || ""}`.trim();
        displayName = fullName !== "" ? fullName : "User";
    }
    
    document.getElementById("userNameBar").textContent = displayName;
    document.getElementById("userIcon").src = activeUser.profilePicture;

    // 3. Render existing requests
    const listContainer = document.getElementById("requestList");
    function renderRequests() {
        listContainer.innerHTML = "";
        if (activeUser.requests) {
            activeUser.requests.forEach(r => {
                const div = document.createElement("div");
                div.className = "request-card";
                div.innerHTML = `
                    <strong style="color: var(--color-csic);">${r.service}</strong><br>
                    <small>Hours: ${r.hours} | Date: ${r.date}</small><br>
                    <p style="font-size:12px; margin-top:5px; color:#555;">${r.comment || 'No comments'}</p>
                `;
                listContainer.appendChild(div);
            });
        }
    }
    renderRequests();

    // 4. Dropdown Menu
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");
    
    profileContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle("hidden");
    });
    document.addEventListener("click", () => dropdownMenu.classList.add("hidden"));

    // 5. Services Accordion
    const serviceButtons = document.querySelectorAll(".service-button");
    serviceButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.stopPropagation();
            this.nextElementSibling.classList.toggle("open");
        });
    });

    // 6. Send Requests
    const btnSend = document.getElementById("btnSendRequest");
    btnSend.addEventListener("click", () => {
        const forms = document.querySelectorAll(".service-form");
        let anyRequest = false;

        forms.forEach(form => {
            const hoursInput = form.querySelector("input[type='number']");
            const commentInput = form.querySelector("input[type='text']");
            const hours = hoursInput.value;
            const service = form.previousElementSibling.textContent;

            if (hours > 0) {
                if (!activeUser.requests) activeUser.requests = [];
                activeUser.requests.push({
                    service: service,
                    hours: hours,
                    comment: commentInput.value,
                    date: new Date().toLocaleDateString()
                });
                anyRequest = true;
                hoursInput.value = "";
                commentInput.value = "";
                form.classList.remove("open");
            }
        });

        if (anyRequest) {
            localStorage.setItem('activeUser', JSON.stringify(activeUser));
            let users = JSON.parse(localStorage.getItem('users')) || [];
            const index = users.findIndex(u => u.email === activeUser.email);
            if (index !== -1) {
                users[index] = activeUser;
                localStorage.setItem('users', JSON.stringify(users));
            }
            renderRequests();
            alert("Request sent successfully.");
        }
    });

    // 7. Navigation
    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('activeUser');
        window.location.href = "/SGO/static/html/ServicioLogin.html";
    });

    document.getElementById("editProfile").addEventListener("click", () => {
        window.location.href = "/SGO/static/html/ServicioEdit.html";
    });
});