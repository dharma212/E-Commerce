let otpToast = null;
// ================= CSRF =================
function getCSRFToken() {

    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];

}


// ================= TOAST =================
function showToast(message, type = "success", autoRemove = true) {

    let container = document.querySelector(".toast-container");

    // CREATE CONTAINER
    if (!container) {

        container = document.createElement("div");

        container.className = "toast-container";

        document.body.appendChild(container);

    }

    // CREATE TOAST
    let toast = document.createElement("div");

    toast.className = `custom-toast ${type}`;

    toast.innerHTML = message;

    container.appendChild(toast);

    // AUTO REMOVE ONLY IF TRUE
    if (autoRemove) {

        setTimeout(() => {

            toast.style.opacity = "0";

            toast.style.transform = "translateX(100%)";

            setTimeout(() => {

                toast.remove();

            }, 500);

        }, 3000);

    }

    // RETURN TOAST
    return toast;

}


// ================= REMOVE DJANGO TOAST =================
document.addEventListener("DOMContentLoaded", function () {

    setTimeout(() => {

        document.querySelectorAll(".custom-toast").forEach(toast => {

            toast.style.opacity = "0";

            toast.style.transform = "translateX(100%)";

            setTimeout(() => {

                toast.remove();

            }, 500);

        });

    }, 3000);

});


// ================= CLEAR ERRORS =================
function clearErrors() {

    document.getElementById(
        "username-error"
    ).innerText = "";

    document.getElementById(
        "email-error"
    ).innerText = "";

    document.getElementById(
        "otp-error"
    ).innerText = "";

}


// ================= SEND OTP =================
function sendOTP() {

    clearErrors();

    let username = document.getElementById(
        "popup_username"
    ).value.trim();

    let email = document.getElementById(
        "popup_email"
    ).value.trim();

    let hasError = false;

    // USERNAME
    if (!username) {

        document.getElementById(
            "username-error"
        ).innerText = "Username is required";

        hasError = true;

    }

    // EMAIL / PHONE
    if (!email) {

        document.getElementById(
            "email-error"
        ).innerText = "Email or Phone is required";

        hasError = true;

    }

    // PHONE VALIDATION
    else if (/^[0-9]+$/.test(email)) {

        // ONLY 10 DIGIT
        if (email.length !== 10) {

            document.getElementById(
                "email-error"
            ).innerText = "Phone number must be 10 digits";

            hasError = true;

        }

        // START 6-9
        else if (!/^[6-9]/.test(email)) {

            document.getElementById(
                "email-error"
            ).innerText = "Enter valid phone number";

            hasError = true;

        }

    }

    if (hasError) {

        return;

    }

    fetch('/api/send-otp/', {

        method: 'POST',

        headers: {

            'Content-Type': 'application/json',

            'X-CSRFToken': getCSRFToken()

        },

        body: JSON.stringify({

            username: username,

            email: email

        })

    })

    .then(res => res.json())

    .then(data => {

        if (data.status === "success") {

            // OTP TOAST
otpToast = showToast(`

    OTP Sent Successfully <br><br>

    <span style="
        background:#fff;
        color:#3d5afe;
        padding:8px 16px;
        border-radius:10px;
        font-size:22px;
        font-weight:bold;
        letter-spacing:3px;
        display:inline-block;
    ">
        ${data.otp}
    </span>

`, "success", false);

            // SHOW OTP BOX
            document.getElementById(
                "popup_step1"
            ).style.display = "none";

            document.getElementById(
                "popup_step2"
            ).style.display = "block";

        }

        else {

            showToast(
                data.message || "Something went wrong",
                "error"
            );

        }

    })

    .catch(error => {

        showToast(
            "Server Error",
            "error"
        );

    });

}


// ================= VERIFY OTP =================
function verifyOTP() {

    clearErrors();

    let email = document.getElementById(
        "popup_email"
    ).value.trim();

    let otp = document.getElementById(
        "popup_otp"
    ).value.trim();

    // EMPTY OTP
    if (!otp) {

        document.getElementById(
            "otp-error"
        ).innerText = "OTP is required";

        return;

    }

    fetch('/api/verify-otp/', {

        method: 'POST',

        headers: {

            'Content-Type': 'application/json',

            'X-CSRFToken': getCSRFToken()

        },

        body: JSON.stringify({

            email: email,

            otp: otp

        })

    })

    .then(res => res.json())

    .then(data => {

        if (data.status === "success") {

            // SUCCESS TOAST
            // REMOVE OTP TOAST
if (otpToast) {

    otpToast.remove();

}

closeLoginModal();

setTimeout(() => {

    window.location.reload();

}, 1000);

        }

        else {

            showToast(
                data.message || "Invalid OTP",
                "error"
            );

        }

    })

    .catch(error => {

        showToast(
            "Server Error",
            "error"
        );

    });

}


// ================= MODAL =================
function openLoginModal() {

    document.getElementById(
        "loginModal"
    ).style.display = "block";

}

function closeLoginModal() {

    document.getElementById(
        "loginModal"
    ).style.display = "none";

}


// ================= AUTO POPUP =================
document.addEventListener("DOMContentLoaded", function () {

    let shown = sessionStorage.getItem(
        "loginPopupShown"
    );

    let isAuthenticated =
        document.body.dataset.authenticated;

    if (isAuthenticated === "false") {

        if (!shown) {

            setTimeout(() => {

                openLoginModal();

                sessionStorage.setItem(
                    "loginPopupShown",
                    "true"
                );

            }, 5000);

        }

    }

});