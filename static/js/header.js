// =========================
// STICKY NAVBAR
// =========================

window.addEventListener("scroll", function(){

    const navbar = document.getElementById(
        "navbar-sticky"
    );

    if(window.scrollY > 180){

        navbar.classList.add(
            "navbar-fixed"
        );

        document.body.classList.add(
            "navbar-spacing"
        );

    }

    else{

        navbar.classList.remove(
            "navbar-fixed"
        );

        document.body.classList.remove(
            "navbar-spacing"
        );

    }

});


// =========================
// PROFILE
// =========================

function goToProfile(){

    window.location.href = "/profile/";

}


// =========================
// CSRF TOKEN
// =========================

function getCSRFToken(){

    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];

}


// =========================
// LOGOUT
// =========================

function logout(){

    fetch('/logout/', {

        method: 'POST',

        headers: {

            'X-CSRFToken': getCSRFToken()

        }

    })

    .then(() => {

        window.location.reload();

    });

}