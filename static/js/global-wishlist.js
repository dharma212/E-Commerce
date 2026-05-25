console.log("GLOBAL WISHLIST LOADED");


/* =========================================
CSRF TOKEN
========================================= */

function getCSRFToken(){

    const token =
        document.querySelector(
            '[name=csrfmiddlewaretoken]'
        );

    return token
        ? token.value
        : "";

}



/* =========================================
TOAST
========================================= */

function showWishlistToast(
    message,
    type="success"
){

    const oldToast =
        document.querySelector(
            ".wishlist-toast"
        );

    if(oldToast){

        oldToast.remove();

    }

    const toast =
        document.createElement("div");

    toast.className =
        `wishlist-toast ${type}`;

    let icon = "";

    if(type === "success"){

        icon =
        `<i class="fa fa-heart mr-2"></i>`;

    }

    else{

        icon =
        `<i class="fa fa-times-circle mr-2"></i>`;

    }

    toast.innerHTML = `
        <div class="wishlist-toast-content">
            ${icon}
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(
        toast
    );

    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    setTimeout(() => {

        toast.classList.remove("show");

        toast.classList.add("hide");

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, 2500);

}



/* =========================================
TOAST STYLE
========================================= */

const wishlistStyle =
document.createElement("style");

wishlistStyle.innerHTML = `

.wishlist-toast{

    position: fixed;

    top: 25px;

    right: 25px;

    min-width: 280px;

    max-width: 350px;

    padding: 16px 20px;

    border-radius: 14px;

    color: #fff;

    font-weight: 600;

    font-size: 15px;

    z-index: 999999;

    opacity: 0;

    transform: translateX(120px);

    transition: all 0.45s ease;

    box-shadow:
    0 10px 30px rgba(0,0,0,0.18);

    backdrop-filter: blur(10px);

}

.wishlist-toast.show{

    opacity: 1;

    transform: translateX(0);

}

.wishlist-toast.hide{

    opacity: 0;

    transform: translateX(120px);

}

/* =========================
SUCCESS = GREEN
========================= */

.wishlist-toast.success{

    background:
    linear-gradient(
        135deg,
        #28a745,
        #1f8a39
    );

}

/* =========================
ERROR = RED
========================= */

.wishlist-toast.error{

    background:
    linear-gradient(
        135deg,
        #dc3545,
        #b02a37
    );

}

.wishlist-toast-content{

    display: flex;

    align-items: center;

    gap: 10px;

}

.wishlist-toast-content i{

    font-size: 20px;

}

`;

document.head.appendChild(
    wishlistStyle
);



/* =========================================
WISHLIST FUNCTION
========================================= */

async function toggleWishlist(
    productId,
    currentButton,
    removeCard=false
){

    // DOUBLE CLICK PREVENT
    if(
        currentButton.dataset.loading === "true"
    ){
        return;
    }

    currentButton.dataset.loading =
        "true";

    try{

        const response =
            await fetch(

                "/api/wishlist/",

                {

                    method: "POST",

                    headers: {

                        "X-CSRFToken":
                        getCSRFToken(),

                        "Content-Type":
                        "application/x-www-form-urlencoded",

                    },

                    body: new URLSearchParams({

                        product_id: productId

                    })

                }

            );

        const data =
            await response.json();

        const icon =
            currentButton.querySelector("i");

        /* =====================================
        UPDATE COUNT
        ===================================== */

        const wishlistCount =
            document.getElementById(
                "wishlist-count"
            );

        if(
            wishlistCount &&
            data.wishlist_count !== undefined
        ){

            wishlistCount.innerText =
                data.wishlist_count;

        }

        /* =====================================
        ADDED
        ===================================== */

        if(data.status === "added"){

            currentButton.classList.remove(
                "btn-outline-dark"
            );

            currentButton.classList.add(
                "btn-danger"
            );

            currentButton.classList.add(
                "active"
            );

            if(icon){

                icon.classList.remove(
                    "far"
                );

                icon.classList.add(
                    "fas"
                );

            }

            showWishlistToast(
                "Added To Wishlist",
                "success"
            );

        }

        /* =====================================
        REMOVED
        ===================================== */

        else if(
            data.status === "removed"
        ){

            currentButton.classList.remove(
                "btn-danger"
            );

            currentButton.classList.remove(
                "active"
            );

            currentButton.classList.add(
                "btn-outline-dark"
            );

            if(icon){

                icon.classList.remove(
                    "fas"
                );

                icon.classList.add(
                    "far"
                );

            }

            // REMOVE CARD
            if(removeCard){

                const card =
                    document.querySelector(
                        `.wishlist-card-${productId}`
                    );

                if(card){

                    card.style.transition =
                        "0.3s";

                    card.style.opacity =
                        "0";

                    card.style.transform =
                        "scale(.8)";

                    setTimeout(() => {

                        card.remove();

                    }, 300);

                }

            }

            showWishlistToast(
                "Removed From Wishlist",
                "error"
            );

        }

    }

    catch(error){

        console.log(error);

        showWishlistToast(
            "Wishlist Error",
            "error"
        );

    }

    finally{

        currentButton.dataset.loading =
            "false";

    }

}



/* =========================================
GLOBAL CLICK
========================================= */

document.addEventListener(
    "click",
    function(e){

        const button =
            e.target.closest(
                ".wishlist-btn, .remove-wishlist-btn"
            );

        if(!button){
            return;
        }

        e.preventDefault();

        const productId =
            button.dataset.productId;

        const removeCard =
            button.classList.contains(
                "remove-wishlist-btn"
            );

        toggleWishlist(
            productId,
            button,
            removeCard
        );

    }
);