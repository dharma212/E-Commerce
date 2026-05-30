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

    window.location.href = "/user-profile/";

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

    // CORE OFF-CANVAS CONTROL FUNCTIONS
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const closeMenuBtn = document.getElementById('closeMenuBtn');
    const navbarCollapse = document.getElementById('navbarCollapse');
    const menuBackdrop = document.getElementById('menuBackdrop');

    function openMenu() {
        navbarCollapse.classList.add('show');
        menuBackdrop.style.display = 'block';
        document.body.classList.add('menu-open');
    }

    function closeMenu() {
        navbarCollapse.classList.remove('show');
        menuBackdrop.style.display = 'none';
        document.body.classList.remove('menu-open');
    }

    if(mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMenu);
    if(closeMenuBtn) closeMenuBtn.addEventListener('click', closeMenu);
    if(menuBackdrop) menuBackdrop.addEventListener('click', closeMenu);

    const mobileHeaderWrapper = document.getElementById('mobileHeaderWrapper');
    const offsetLimit = 90;

    window.addEventListener('scroll', function() {
        if (window.innerWidth >= 992) {
            mobileHeaderWrapper.classList.remove('sticky-active');
            return; 
        }

        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;

        if (currentScroll > offsetLimit) {
            mobileHeaderWrapper.classList.add('sticky-active');
        } else {
            mobileHeaderWrapper.classList.remove('sticky-active');
        }
    });

    // LIVE AUTOCOMPLETE AJAX SEARCH ALGORITHM
    function setupAsynchronousSearch(fieldId, outputPanelId) {
        const targetInput = document.getElementById(fieldId);
        const feedbackBox = document.getElementById(outputPanelId);
        let liveDebounce;

        if(!targetInput || !feedbackBox) return;

        targetInput.addEventListener("keyup", function () {
            clearTimeout(liveDebounce);
            let stringQuery = this.value.trim();

            if (stringQuery.length < 1) {
                feedbackBox.style.display = "none";
                return;
            }

            liveDebounce = setTimeout(() => {
                fetch(`/search-product/?search=${stringQuery}`)
                    .then(res => res.json())
                    .then(collection => {
                        let matches = collection.products;
                        let structuralHtml = "";

                        if (matches.length > 0) {
                            matches.forEach(row => {
                                structuralHtml += `
                                <a href="/product/${row.id}/" class="search-product-item">
                                    <img src="${row.image}">
                                    <div class="search-product-info">
                                        <div class="search-product-name">${row.name}</div>
                                        <div class="search-product-price">₹${row.price}</div>
                                    </div>
                                </a>`;
                            });
                        } else {
                            structuralHtml = `<div class="p-3 text-center text-muted">No Product Found</div>`;
                        }

                        feedbackBox.innerHTML = structuralHtml;
                        feedbackBox.style.display = "block";
                    });
            }, 400);
        });
    }

    setupAsynchronousSearch("search-input", "search-result-box");
    setupAsynchronousSearch("search-input-mobile", "search-result-box-mobile");

    document.addEventListener("click", function (event) {
        if (!document.getElementById("main-header").contains(event.target)) {
            const out1 = document.getElementById("search-result-box");
            const out2 = document.getElementById("search-result-box-mobile");
            if(out1) out1.style.display = "none";
            if(out2) out2.style.display = "none";
        }
    });