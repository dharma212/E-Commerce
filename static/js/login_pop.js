// ================= CSRF =================
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}


// ================= SEND OTP =================
function sendOTP() {

    let username = document.getElementById("popup_username").value;
    let email = document.getElementById("popup_email").value;

    if (!username || !email) {
        alert("Enter username and email");
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

            alert("OTP sent");

            document.getElementById("popup_step1").style.display = "none";
            document.getElementById("popup_step2").style.display = "block";

        } else {
            alert(data.message);
        }

    });

}


// ================= VERIFY OTP =================
function verifyOTP() {

    let email = document.getElementById("popup_email").value;
    let otp = document.getElementById("popup_otp").value;

    if (!otp) {
        alert("Enter OTP");
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

            alert("Login success 🎉");

            closeLoginModal();

            window.location.reload();

        } else {
            alert(data.message);
        }

    });

}


// ================= MODAL =================
function openLoginModal() {
    document.getElementById("loginModal").style.display = "block";
}

function closeLoginModal() {
    document.getElementById("loginModal").style.display = "none";
}


// ================= AUTO POPUP =================
document.addEventListener("DOMContentLoaded", function () {

    let shown = sessionStorage.getItem("loginPopupShown");

    // check login from body attribute
    let isAuthenticated = document.body.dataset.authenticated;

    if (isAuthenticated === "false") {

        if (!shown) {

            setTimeout(() => {

                openLoginModal();

                sessionStorage.setItem("loginPopupShown", "true");

            }, 5000);

        }

    }

});