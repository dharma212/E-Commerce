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
MODERN TOAST
========================================= */

function showCartToast(
    message,
    type = "success"
){

    // REMOVE OLD
    const oldToast =
        document.querySelector(
            ".cart-toast"
        );

    if(oldToast){

        oldToast.remove();

    }

    // TOAST
    const toast =
        document.createElement("div");

    toast.className =
        `cart-toast ${type}`;

    // ICON
    let icon = "";

    if(type === "success"){

        icon =
        `<i class="fa fa-check-circle mr-2"></i>`;

    }

    else if(type === "error"){

        icon =
        `<i class="fa fa-times-circle mr-2"></i>`;

    }

    else{

        icon =
        `<i class="fa fa-info-circle mr-2"></i>`;

    }

    toast.innerHTML = `
        <div class="toast-content">
            ${icon}
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // SHOW
    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    // HIDE
    setTimeout(() => {

        toast.classList.remove("show");

        toast.classList.add("hide");

        setTimeout(() => {

            toast.remove();

        }, 500);

    }, 2500);

}



/* =========================================
TOAST CSS
========================================= */

const toastStyle =
document.createElement("style");

toastStyle.innerHTML = `

.cart-toast{

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

.cart-toast.show{

    opacity: 1;

    transform: translateX(0);

}

.cart-toast.hide{

    opacity: 0;

    transform: translateX(120px);

}

.cart-toast.success{

    background:
    linear-gradient(
        135deg,
        #28a745,
        #1f8a39
    );

}

.cart-toast.error{

    background:
    linear-gradient(
        135deg,
        #dc3545,
        #b02a37
    );

}

.cart-toast.info{

    background:
    linear-gradient(
        135deg,
        #007bff,
        #0056b3
    );

}

.toast-content{

    display: flex;

    align-items: center;

    gap: 10px;

}

.toast-content i{

    font-size: 20px;

}

`;

document.head.appendChild(toastStyle);



/* =========================================
GLOBAL CART
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

        // DOUBLE CLICK PREVENT
        if(
            button.dataset.loading === "true"
        ){
            return;
        }

        button.dataset.loading =
            "true";

        const productId =
            button.dataset.id;

        // =====================================
        // QUANTITY
        // =====================================

        let quantity = 1;

        // DETAILS PAGE
        if(
            button.classList.contains("px-3")
        ){

            const quantityInput =
                document.querySelector(
                    ".quantity input"
                );

            if(quantityInput){

                quantity =
                parseInt(
                    quantityInput.value
                );

                if(
                    isNaN(quantity)
                    || quantity < 1
                ){

                    quantity = 1;

                }

                const maxStock =
                parseInt(
                    quantityInput.dataset.stock
                );

                // MAX STOCK
                if(quantity > maxStock){

                    quantity = maxStock;

                }

            }

        }

        // LOADING
        const oldHtml =
            button.innerHTML;

        button.disabled = true;

        button.innerHTML = `
            <span class="spinner-border spinner-border-sm"></span>
        `;

        try{

            const response =
                await fetch(
                    `/cart/add/${productId}/`,
                    {
                        method:"POST",

                        headers:{

                            "Content-Type":
                            "application/json",

                            "X-CSRFToken":
                            getCSRFToken(),

                            "X-Requested-With":
                            "XMLHttpRequest"

                        },

                        body: JSON.stringify({

                            quantity: quantity

                        })

                    }
                );

            const data =
                await response.json();

            // =====================================
            // CART COUNT
            // =====================================

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

            // =====================================
            // ADDED
            // =====================================

            if(
                data.status === "added"
            ){

                // DETAIL PAGE BUTTON
                if(
                    button.classList.contains(
                        "px-3"
                    )
                ){

                    button.classList.remove(
                        "btn-primary"
                    );

                    button.classList.add(
                        "btn-success"
                    );

                    button.innerHTML = `
                        <i class="fa fa-check mr-1"></i>
                        Added To Cart
                    `;

                }

                // SHOP PAGE BUTTON
                else{

                    button.classList.remove(
                        "btn-outline-dark"
                    );

                    button.classList.add(
                        "btn-warning"
                    );

                    button.innerHTML = `
                        <i class="fa fa-shopping-cart"></i>
                    `;

                }

                showCartToast(
                    `Added ${quantity} item(s) to cart`,
                    "success"
                );

            }

            // =====================================
            // REMOVED
            // =====================================

            else if(
                data.status === "removed"
            ){

                // DETAIL PAGE
                if(
                    button.classList.contains(
                        "px-3"
                    )
                ){

                    button.classList.remove(
                        "btn-success"
                    );

                    button.classList.add(
                        "btn-primary"
                    );

                    button.innerHTML = `
                        <i class="fa fa-shopping-cart mr-1"></i>
                        Add To Cart
                    `;

                }

                // SHOP PAGE
                else{

                    button.classList.remove(
                        "btn-warning"
                    );

                    button.classList.add(
                        "btn-outline-dark"
                    );

                    button.innerHTML = `
                        <i class="fa fa-shopping-cart"></i>
                    `;

                }

                showCartToast(
                    "Removed From Cart",
                    "error"
                );

            }

            else{

                button.innerHTML = oldHtml;

                showCartToast(
                    "Something Went Wrong",
                    "error"
                );

            }

        }

        catch(error){

            console.log(error);

            button.innerHTML =
                oldHtml;

            showCartToast(
                "Server Error",
                "error"
            );

        }

        finally{

            button.disabled = false;

            button.dataset.loading =
                "false";

        }

    }
);