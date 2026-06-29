(function () {
        let activeSystemToastTracker = null;

    // ================= =================
    function getAuthenticationCSRFToken() {
        return document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken'))
            ?.split('=')[1];
    }

    // ================= =================
    function showGlobalToastMessage(message, type = "success", autoRemove = true) {
        if (!autoRemove && activeSystemToastTracker) {
            activeSystemToastTracker.remove();
        }

        let container = document.querySelector(".toast-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";
            document.body.appendChild(container);
        }

        let toast = document.createElement("div");
        toast.className = `custom-toast ${type}`;
        toast.innerHTML = message;
        container.appendChild(toast);

        if (autoRemove) {
            setTimeout(() => {
                toast.style.opacity = "0";
                toast.style.transform = "translateX(100%)";
                setTimeout(() => { toast.remove(); }, 500);
            }, 5000);
        } else {
            activeSystemToastTracker = toast;
        }
        return toast;
    }

    // =================  =================
    function clearAllModalFormErrors() {
        const errorFields = [
            "username-error", "email-error", "otp-error",
            "signup-username-error", "signup-firstname-error", 
            "signup-lastname-error", "signup-email-error", "signup-phone-error"
        ];
        errorFields.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.innerText = "";
        });
    }

    // =================  =================
    window.openLoginModal = function() {
        clearAllModalFormErrors();
        if (document.getElementById("popup_step1")) document.getElementById("popup_step1").style.display = "block";
        if (document.getElementById("popup_step2")) document.getElementById("popup_step2").style.display = "none";
        
        const signupModal = document.getElementById("signupModal");
        const loginModal = document.getElementById("loginModal");
        
        if (signupModal) signupModal.style.display = "none";
        if (loginModal) loginModal.style.display = "flex";
    };

    window.closeLoginModal = function() {
        const loginModal = document.getElementById("loginModal");
        if (loginModal) loginModal.style.display = "none";
        if (activeSystemToastTracker) { activeSystemToastTracker.remove(); } 
    };

    window.openSignupModal = function() {
        clearAllModalFormErrors();
        const loginModal = document.getElementById("loginModal");
        const signupModal = document.getElementById("signupModal");
        
        if (loginModal) loginModal.style.display = "none";
        if (signupModal) signupModal.style.display = "flex";
    };

    window.closeSignupModal = function() {
        const signupModal = document.getElementById("signupModal");
        if (signupModal) signupModal.style.display = "none";
    };

    // ================= ૧. SIGNUP =================
    window.processSignupAndGoToLogin = function() {
        clearAllModalFormErrors();

        const username = document.getElementById("signup_username").value.trim();
        const firstname = document.getElementById("signup_firstname").value.trim();
        const lastname = document.getElementById("signup_lastname").value.trim();
        const email = document.getElementById("signup_email").value.trim();
        const phone = document.getElementById("signup_phone").value.trim();
        let hasError = false;

        if (!username) { document.getElementById("signup-username-error").innerText = "Username is required"; hasError = true; }
        if (!firstname) { document.getElementById("signup-firstname-error").innerText = "First Name is required"; hasError = true; }
        if (!lastname) { document.getElementById("signup-lastname-error").innerText = "Last Name is required"; hasError = true; }
        if (!email) { document.getElementById("signup-email-error").innerText = "Email is required"; hasError = true; }
        if (!phone) {
            document.getElementById("signup-phone-error").innerText = "Phone number is required";
            hasError = true;
        } else if (phone.length !== 10 || !/^[6-9]/.test(phone)) {
            document.getElementById("signup-phone-error").innerText = "Enter a valid 10-digit phone number";
            hasError = true;
        }

        if (hasError) return;

        fetch('/api/send-otp/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getAuthenticationCSRFToken()
            },
            body: JSON.stringify({
                username: username, first_name: firstname, last_name: lastname, email: email, phone: phone, is_signup: true
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.otp) {
                showGlobalToastMessage(`
                    <strong>Registration Successful!</strong><br>
                    <span>Use this Security OTP to Login:</span><br>
                    <span style="display:inline-block; background:#16a34a; color:#fff; padding:6px 14px; border-radius:6px; font-size:20px; font-weight:bold; margin-top:6px; letter-spacing:3px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                        ${data.otp}
                    </span>
                `, "success", false); 

                window.closeSignupModal();
                window.openLoginModal();

                if (document.getElementById("popup_username")) document.getElementById("popup_username").value = username;
                if (document.getElementById("popup_email")) document.getElementById("popup_email").value = email;

                if (document.getElementById("popup_step1")) document.getElementById("popup_step1").style.display = "none";
                if (document.getElementById("popup_step2")) document.getElementById("popup_step2").style.display = "block";
            } else {
                showGlobalToastMessage(data.message || "Signup failed", "error");
            }
        })
        .catch(() => { showGlobalToastMessage("Server Error during signup", "error"); });
    };

    // ================= ૨. LOGIN સિસ્ટમ (Send OTP બટન લોજિક) =================
    window.sendOTP = function() {
        clearAllModalFormErrors();

        const username = document.getElementById("popup_username").value.trim();
        const email = document.getElementById("popup_email").value.trim();
        let hasError = false;

        if (!username) { document.getElementById("username-error").innerText = "Username is required"; hasError = true; }
        if (!email) { document.getElementById("email-error").innerText = "Email is required"; hasError = true; }

        if (hasError) return;

        fetch('/api/send-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getAuthenticationCSRFToken()
            },
            body: JSON.stringify({ username: username, email: email, is_signup: false })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.otp) {
                showGlobalToastMessage(`
                    <strong>OTP Sent Successfully!</strong><br>
                    <span>Your Security OTP Code is:</span><br>
                    <span style="display:inline-block; background:#16a34a; color:#fff; padding:6px 14px; border-radius:6px; font-size:20px; font-weight:bold; margin-top:6px; letter-spacing:3px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                        ${data.otp}
                    </span>
                `, "success", false);

                if (document.getElementById("popup_step1")) document.getElementById("popup_step1").style.display = "none";
                if (document.getElementById("popup_step2")) document.getElementById("popup_step2").style.display = "block";
            } else {
                showGlobalToastMessage(data.message || "Login failed", "error", true);
            }
        })
        .catch(() => { showGlobalToastMessage("Server communication error", "error", true); });
    };

    // ================= ૩. OTP VERIFICATION =================
    window.verifyOTP = function() {
        clearAllModalFormErrors();
        const email = document.getElementById("popup_email").value.trim();
        const otp = document.getElementById("popup_otp").value.trim();

        if (!otp) {
            document.getElementById("otp-error").innerText = "OTP token is required";
            return;
        }

        fetch('/api/verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getAuthenticationCSRFToken()
            },
            body: JSON.stringify({ email: email, otp: otp })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                if (activeSystemToastTracker) { activeSystemToastTracker.remove(); }
                
                window.closeLoginModal();
                showGlobalToastMessage("Welcome back! Login Successful.", "success", true);
                setTimeout(() => { window.location.reload(); }, 1200);
            } else {
                showGlobalToastMessage(data.message || "Invalid OTP entered", "error", true);
            }
        })
        .catch(() => { showGlobalToastMessage("Verification system error", "error", true); });
    };

})();
function showGlobalToastMessage(message, type = "success", autoRemove = true) {
    let container = document.querySelector(".toast-container");
    
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    let toast = document.createElement("div");
    toast.className = `custom-toast ${type}`;
    toast.innerHTML = message;
    container.appendChild(toast);

    if (autoRemove) {
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            setTimeout(() => { toast.remove(); }, 500);
        }, 5000);
    }
    return toast;
}