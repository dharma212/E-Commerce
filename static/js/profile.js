let currentField = null;
let editTimer = null;

/* ================= TOAST ================= */
function showToast(msg, type = "success") {
    const old = document.querySelector(".toast-box");
    if (old) old.remove();

    const icons = {
        success: '<i class="bi bi-check-circle-fill"></i>',
        error: '<i class="bi bi-x-circle-fill"></i>',
        warning: '<i class="bi bi-exclamation-triangle-fill"></i>'
    };

    const colors = {
        success: "#2ecc71",
        error: "#e74c3c",
        warning: "#f39c12"
    };

    const t = document.createElement("div");
    t.className = "toast-box";

    t.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px">${icons[type]}</span>
            <span>${msg}</span>
        </div>
    `;

    Object.assign(t.style, {
        position: "fixed",
        top: "20px",
        right: "20px",
        background: colors[type],
        color: "#fff",
        padding: "12px 18px",
        borderRadius: "10px",
        boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
        zIndex: "9999999",
        fontSize: "14px",
        animation: "slideIn 0.3s ease"
    });

    document.body.appendChild(t);

    setTimeout(() => {
        t.style.opacity = "0";
        t.style.transform = "translateX(100%)";
        t.style.transition = "0.3s";
        setTimeout(() => t.remove(), 300);
    }, 3000);
}

/* ================= CSRF ================= */
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(r => r.startsWith('csrftoken'))?.split('=')[1];
}

/* ================= LOAD USER ================= */
async function loadUser() {
    try {
        const res = await fetch("/api/user-profile/", {
            method: "GET",
            credentials: "include"
        });

        if (!res.ok) throw new Error();

        const data = await res.json();

        ["username","email","first_name","last_name","phone","city","bio"]
        .forEach(f => {
            const input = document.getElementById(f);
            const text = document.getElementById(f + "Text");

            if (input) input.value = data[f] || "";
            if (text) text.innerText = data[f] || "--";
        });

        if (data.image) {
            profileImage.src = data.image;
            profileImage.style.display = "block";
            avatarText.style.display = "none";
        }

        updateName();
        updateProgress();

    } catch {
        showToast("Failed to load profile", "error");
    }
}

/* ================= EDIT ================= */
function enableEdit(id) {
    if (currentField) return;

    currentField = id;

    const input = document.getElementById(id);
    const text = document.getElementById(id + "Text");

    input.classList.remove("d-none");
    text.parentElement.style.display = "none";

    input.value = text.innerText === "--" ? "" : text.innerText;
    input.focus();

}

/* ================= SAVE ================= */
async function saveField(id) {
    const input = document.getElementById(id);
    const errBox = document.getElementById(id + "Error");

    const fieldNames = {
        username: "Username",
        email: "Email",
        first_name: "First name",
        last_name: "Last name",
        phone: "Phone number",
        city: "City",
        bio: "Bio"
    };

    const value = input.value.trim();
    const label = fieldNames[id];

    if (!value) {
        const msg = `${label} is required`;
        errBox.innerText = msg;
        input.classList.add("is-invalid");
        showToast(msg, "warning");
        return false;
    }

    if (id === "email" && !/^\S+@\S+\.\S+$/.test(value)) {
        return error("Enter valid email");
    }

    if (id === "phone" && !/^[0-9]{10}$/.test(value)) {
        return error("Phone must be 10 digits");
    }

    function error(msg){
        errBox.innerText = msg;
        input.classList.add("is-invalid");
        showToast(msg, "warning");
        return false;
    }

    errBox.innerText = "";
    input.classList.remove("is-invalid");

    try {
        const res = await fetch("/api/user-profile/", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ [id]: value })
        });

        const data = await res.json();

        if (!res.ok) {
            const msg = data[id]?.[0] || "Update failed";
            showToast(msg, "error");
            return false;
        }

        showToast(`${label} updated successfully`, "success");

        document.getElementById(id + "Text").innerText = value;

        updateName();
        updateProgress();

        return true;

    } catch {
        showToast("Network error", "error");
        return false;
    }
}

/* ================= CLICK OUTSIDE ================= */
document.addEventListener("click", async (e) => {
    if (!currentField) return;

    const input = document.getElementById(currentField);
    const text = document.getElementById(currentField + "Text");

    if (!input || input.contains(e.target)) return;

    const changed = input.value !== text.innerText;

    if (changed) {
        const ok = await saveField(currentField);
        if (!ok) return;
    }

    disableEdit();
});

/* ================= ENTER KEY ================= */
document.addEventListener("keydown", async (e) => {
    if (e.key === "Enter" && currentField) {
        e.preventDefault();

        const ok = await saveField(currentField);
        if (!ok) return;

        disableEdit();
    }
});

/* ================= DISABLE ================= */
function disableEdit() {
    const input = document.getElementById(currentField);
    const text = document.getElementById(currentField + "Text");

    input.classList.add("d-none");
    text.parentElement.style.display = "block";

    clearTimeout(editTimer);
    currentField = null;
}

/* ================= NAME ================= */
function updateName() {
    const name = (first_name.value + " " + last_name.value).trim();
    displayName.innerText = name || "Your Name";
    avatarText.innerText = displayName.innerText.charAt(0).toUpperCase();
}

/* ================= PROGRESS ================= */
function updateProgress() {
    const fields = ["username","email","first_name","last_name","phone","city","bio"];

    const filled = fields.filter(f =>
        document.getElementById(f).value.trim()
    ).length;

    const percent = Math.floor((filled / fields.length) * 100);

    progressBar.style.width = percent + "%";
    progressText.innerText = percent + "%";
}

/* ================= IMAGE ================= */
function openImageModal() {
    const modal = document.getElementById("imageModal");
    const popupImage = document.getElementById("popupImage");

    modal.style.display = "flex";

    if (profileImage && profileImage.src && profileImage.style.display !== "none") {
        popupImage.src = profileImage.src;
    } else {
        popupImage.src = "/static/img/download.jpg";
    }
}

function closeImageModal() {
    document.getElementById("imageModal").style.display = "none";
}

async function uploadImage() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];

    if (!file) {
        showToast("Select image", "warning");
        return;
    }

    const form = new FormData();
    form.append("image", file);

    const res = await fetch("/api/upload-image/", {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRFToken": getCSRFToken() },
        body: form
    });

    const data = await res.json();

    if (res.ok) {
        profileImage.src = data.image;
        profileImage.style.display = "block";
        avatarText.style.display = "none";

        // ✅ reset input (IMPORTANT)
        input.value = "";

        showToast("Image updated successfully");
        closeImageModal();
    } else {
        showToast("Upload failed", "error");
    }
}

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
    window.profileImage = document.getElementById("profileImage");
    window.avatarText = document.getElementById("avatarText");
    window.displayName = document.getElementById("displayName");
    window.progressBar = document.getElementById("progressBar");
    window.progressText = document.getElementById("progressText");
    window.first_name = document.getElementById("first_name");
    window.last_name = document.getElementById("last_name");

    // image preview
    const imageInput = document.getElementById("imageInput");
const popupImage = document.getElementById("popupImage");

imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (file) {
        const previewURL = URL.createObjectURL(file);

        popupImage.src = previewURL;
        popupImage.style.display = "block";

        // Optional: free memory
        popupImage.onload = () => URL.revokeObjectURL(previewURL);
    }
});

    loadUser();
});