console.log("GLOBAL CART LOADED");

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

function showCartToast(
    message,
    type="success"
){

    const oldToast =
        document.querySelector(
            ".global-cart-toast"
        );

    if(oldToast){
        oldToast.remove();
    }

    const toast =
        document.createElement("div");

    toast.className =
        "global-cart-toast";

    toast.innerText =
        message;

    toast.style.position =
        "fixed";

    toast.style.top =
        "20px";

    toast.style.right =
        "20px";

    toast.style.padding =
        "14px 20px";

    toast.style.borderRadius =
        "10px";

    toast.style.color =
        "#fff";

    toast.style.fontWeight =
        "600";

    toast.style.zIndex =
        "999999";

    toast.style.background =
        type === "error"
        ? "#dc3545"
        : "#28a745";

    document.body.appendChild(
        toast
    );

    setTimeout(() => {

        toast.remove();

    }, 2500);

}

/* =========================================
GLOBAL TOGGLE CART
========================================= */

document.addEventListener(
    "click",
    async function(e){

        const button =
            e.target.closest(
                ".add-to-cart"
            );

        if(!button){
            return;
        }

        e.preventDefault();

        /* =====================================
        PREVENT DOUBLE CLICK
        ===================================== */

        if(
            button.dataset.loading === "true"
        ){
            return;
        }

        button.dataset.loading =
            "true";

        const productId =
            button.dataset.id;

        try{

            const response =
                await fetch(
                    `/cart/add/${productId}/`,
                    {
                        method:"POST",

                        headers:{
                            "X-CSRFToken":
                            getCSRFToken(),

                            "X-Requested-With":
                            "XMLHttpRequest"
                        }
                    }
                );

            const data =
                await response.json();

            /* =====================================
            UPDATE CART COUNT
            ===================================== */

            const cartCount =
                document.getElementById(
                    "cart-count"
                );

            if(
                cartCount &&
                data.cart_count !== undefined
            ){

                cartCount.innerText =
                    data.cart_count;

            }

            /* =====================================
            TOGGLE BUTTON
            ===================================== */

            if(data.status === "added"){

                button.classList.add(
                    "active-cart-btn"
                );

                button.classList.remove(
                    "btn-outline-dark"
                );

                button.classList.add(
                    "btn-warning"
                );

                showCartToast(
                    "Added To Cart"
                );

            }

            else if(
                data.status === "removed"
            ){

                button.classList.remove(
                    "active-cart-btn"
                );

                button.classList.remove(
                    "btn-warning"
                );

                button.classList.add(
                    "btn-outline-dark"
                );

                showCartToast(
                    "Removed From Cart",
                    "error"
                );

            }

        }catch(error){

            console.log(error);

            showCartToast(
                "Cart Error",
                "error"
            );

        }

        finally{

            button.dataset.loading =
                "false";

        }

    }
);