/* =========================================
CSRF TOKEN
========================================= */

function getCSRFToken() {

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
) {

    // REMOVE OLD
    const oldToast =
        document.querySelector(
            ".cart-toast"
        );

    if (oldToast) {

        oldToast.remove();

    }

    // TOAST
    const toast =
        document.createElement("div");

    toast.className =
        `cart-toast ${type}`;

    // ICON
    let icon = "";

    if (type === "success") {

        icon =
            `<i class="fa fa-check-circle mr-2"></i>`;

    }

    else if (type === "error") {

        icon =
            `<i class="fa fa-times-circle mr-2"></i>`;

    }

    else {

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
    async function (e) {

        const button =
            e.target.closest(".add-to-cart, .buy-now");
        popupAction = button.classList.contains("buy-now")
            ? "buy"
            : "cart";
        if (!button) {
            return;
        }

        e.preventDefault();

        // DOUBLE CLICK PREVENT
        if (
            button.dataset.loading === "true"
        ) {
            return;
        }

        button.dataset.loading =
            "true";

        const productId =
            button.dataset.id;
        // PRODUCT HAS VARIANTS ?
        const hasColors =
            button.dataset.colors &&
            button.dataset.colors.trim() !== "";

        const hasSizes =
            button.dataset.sizes &&
            button.dataset.sizes.trim() !== "";

        // OPEN POPUP FIRST
        if (hasColors || hasSizes) {

            popupProductId = productId;
            const nameEl = document.getElementById("popupProductName");
            if (nameEl) {
                nameEl.innerText = btn.dataset.name;
            }

            const colorsDiv =
                document.getElementById("popupColors");

            const sizesDiv =
                document.getElementById("popupSizes");

            colorsDiv.innerHTML = "";
            sizesDiv.innerHTML = "";

            (button.dataset.colors || "")
                .split(",")
                .forEach(color => {

                    color = color.trim();

                    if (color) {
                        colorsDiv.innerHTML += `
                <span class="variant-option">
                    ${color}
                </span>
            `;
                    }

                });

            (button.dataset.sizes || "")
                .split(",")
                .forEach(size => {

                    size = size.trim();

                    if (size) {
                        sizesDiv.innerHTML += `
                <span class="variant-option">
                    ${size}
                </span>
            `;
                    }

                });

            const variantPopup =
                document.getElementById("variantPopup");

            if (variantPopup) {
                variantPopup.style.display = "flex";
            }

            button.dataset.loading = "false";

            return; // IMPORTANT
        }
        const isInCart =
            button.classList.contains(
                "active-cart-btn"
            );
        if (
            popupAction === "cart" &&
            isInCart &&
            button.classList.contains("px-3")
        ) {
            window.location.href = "/cart/";
            return;
        }
        // =====================================
        // QUANTITY
        // =====================================

        let quantity = 1;

        // DETAILS PAGE
        if (
            button.classList.contains("px-3")
        ) {

            const quantityInput =
                document.querySelector(
                    ".quantity input"
                );

            if (quantityInput) {

                quantity =
                    parseInt(
                        quantityInput.value
                    );

                if (
                    isNaN(quantity)
                    || quantity < 1
                ) {

                    quantity = 1;

                }

                const maxStock =
                    parseInt(
                        quantityInput.dataset.stock
                    );

                // MAX STOCK
                if (quantity > maxStock) {

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

        try {
            let selectedColor = "";
            let selectedSize = "";

            /* COLOR */

            const activeColor =
                document.querySelector(".color-box.active");

            if (activeColor) {

                selectedColor =
                    activeColor.dataset.color ||
                    activeColor.getAttribute("data-color") ||
                    activeColor.title ||
                    "";
            }

            /* SIZE */

            const activeSize =
                document.querySelector(".size-badge.active");

            if (activeSize) {

                selectedSize =
                    activeSize.dataset.size ||
                    activeSize.getAttribute("data-size") ||
                    activeSize.innerText.trim() ||
                    "";
            }

            /* VALIDATION */

            const hasColor = document.querySelectorAll(".color-box").length > 0;
            const hasSize = document.querySelectorAll(".size-badge").length > 0;

            if ((hasColor && !selectedColor) || (hasSize && !selectedSize)) {

                button.disabled = false;
                button.dataset.loading = "false";
                button.innerHTML = oldHtml;

                // OPEN POPUP
                if ($("#variantModal").length) {

                    currentProductId = productId;
                    actionType = "cart";

                    $("#variantModal").fadeIn();
                }

                return;
            }

            const response =
                await fetch(
                    `/cart/add/${productId}/`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                            "X-Requested-With": "XMLHttpRequest"
                        },

                        body: JSON.stringify({

                            quantity: quantity,

                            color: selectedColor,

                            size: selectedSize

                        })
                    }
                );

            const data = await response.json();

            // =====================================
            // CART COUNT
            // =====================================

            const cartCount =
                document.getElementById(
                    "cart-count"
                );

            if (
                cartCount &&
                data.cart_count !== undefined
            ) {

                cartCount.innerText =
                    data.cart_count;

            }

            // =====================================
            // ADDED
            // =====================================

            if (
                data.status === "added"
            ) {

                // DETAIL PAGE BUTTON
                if (
                    button.classList.contains(
                        "px-3"
                    )
                ) {

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
                else {

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

            else if (
                data.status === "removed"
            ) {

                // DETAIL PAGE
                if (
                    button.classList.contains(
                        "px-3"
                    )
                ) {

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
                else {

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

            else {

                button.innerHTML = oldHtml;

                showCartToast(
                    "Something Went Wrong",
                    "error"
                );

            }

        }

        catch (error) {

            console.log(error);

            button.innerHTML =
                oldHtml;

            showCartToast(
                "Server Error",
                "error"
            );

        }

        finally {

            button.disabled = false;

            button.dataset.loading =
                "false";

        }

    }
);
/* =========================================
VARIANT POPUP CONTINUE
========================================= */

let popupProductId = null;
let popupAction = "cart";
document.addEventListener("click", function (e) {

    const continueBtn =
        e.target.closest("#continueBtn");

    if (!continueBtn) {
        return;
    }

    e.preventDefault();

    const activeColor =
        document.querySelector(
            "#popupColors .variant-option.active"
        );

    const activeSize =
        document.querySelector(
            "#popupSizes .variant-option.active"
        );

    const selectedColor =
        activeColor
            ? activeColor.innerText.trim()
            : "";

    const selectedSize =
        activeSize
            ? activeSize.innerText.trim()
            : "";

    if (!selectedColor) {

        showCartToast(
            "Please select color",
            "error"
        );

        return;
    }

    if (!selectedSize) {

        showCartToast(
            "Please select size",
            "error"
        );

        return;
    }

    fetch(
        `/cart/add/${popupProductId}/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },

            body: JSON.stringify({

                quantity: 1,
                color: selectedColor,
                size: selectedSize

            })
        }
    )

        .then(res => res.json())

        .then(data => {

            if (data.status === "added") {

                document.getElementById(
                    "variantPopup"
                ).style.display = "none";

                // BUY NOW CLICK HATU ?
                if (popupAction === "buy") {

                    window.location.href = "/checkout/";
                    return;
                }

                // NORMAL ADD TO CART
                showCartToast(
                    `${selectedColor} / ${selectedSize} Added To Cart`,
                    "success"
                );

                const cartCount =
                    document.getElementById(
                        "cart-count"
                    );

                if (
                    cartCount &&
                    data.cart_count !== undefined
                ) {

                    cartCount.innerText =
                        data.cart_count;

                }

            } else {

                showCartToast(
                    "Something Went Wrong",
                    "error"
                );

            }

        })
        .catch(() => {

            showCartToast(
                "Server Error",
                "error"
            );

        });

});
let defaultProductImage = "";

document.addEventListener("click", function (e) {
    const btn = e.target.closest(".add-to-cart");
    if (!btn) return;

    e.preventDefault();

    const hasColors = btn.dataset.colors && btn.dataset.colors.trim() !== "";
    const hasSizes = btn.dataset.sizes && btn.dataset.sizes.trim() !== "";

    if (!hasColors && !hasSizes) {
        return;
    }

    e.preventDefault();
    e.stopImmediatePropagation();

    popupProductId = btn.dataset.id;
    document.getElementById("popupProductName").innerText =
        btn.dataset.name;

    let mainProductImg = btn.dataset.image;
    if (!mainProductImg || mainProductImg === "" || mainProductImg.includes("None")) {
        const productCard = btn.closest(".product-item, .card, .product-card");
        if (productCard) {
            const cardImg = productCard.querySelector("img");
            if (cardImg) mainProductImg = cardImg.src;
        }
    }
    defaultProductImage = mainProductImg || "/static/img/no-image.png";
    const popupImg =
        document.getElementById("popupProductImage");

    if (popupImg) {
        popupImg.src = defaultProductImage;
    }

    const colorsDiv = document.getElementById("popupColors");
    const sizesDiv = document.getElementById("popupSizes");

    colorsDiv.innerHTML = "";
    sizesDiv.innerHTML = "";

    let colorImageMap = {};
    if (btn.dataset.colorImages) {
        btn.dataset.colorImages.split(",").forEach(item => {
            const parts = item.split(":");
            if (parts.length >= 2) {
                const cName = parts[0].trim().toLowerCase();
                const cUrl = parts.slice(1).join(":").trim();
                if (cName && cUrl) {
                    colorImageMap[cName] = cUrl;
                }
            }
        });
    }

    (btn.dataset.colors || "").split(",").forEach(color => {
        color = color.trim();
        if (color) {
            const lowerColor = color.toLowerCase();
            const finalColorImg = colorImageMap[lowerColor] ? colorImageMap[lowerColor] : defaultProductImage;

            colorsDiv.innerHTML += `
                <span class="variant-option" data-color-img="${finalColorImg}">
                    <img src="${finalColorImg}" alt="${color}" onerror="this.src='${defaultProductImage}'">
                    ${color}
                </span>
            `;
        }
    });

    (btn.dataset.sizes || "").split(",").forEach(size => {
        size = size.trim();
        if (size) {
            sizesDiv.innerHTML += `
                <span class="variant-option">
                    ${size}
                </span>
            `;
        }
    });

    document.getElementById("variantPopup").style.display = "flex";
});

/* ========================================= */
let wishlistDefaultImage = "";

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".wishlist-add-to-cart");

    if (!btn) return;

    e.preventDefault();

    popupProductId = btn.dataset.id;
    popupAction = "cart";

    document.getElementById("popupProductName").innerText =
        btn.dataset.name || "";

    wishlistDefaultImage = btn.dataset.image || "";
    let firstColorImage = wishlistDefaultImage;

    if (btn.dataset.colorImages) {

        const items = btn.dataset.colorImages
            .split(",")
            .map(i => i.trim())
            .filter(i => i.includes(":"));

        for (let i = 0; i < items.length; i++) {

            const index = items[i].indexOf(":");
            const color = items[i].substring(0, index).trim();
            const img = items[i].substring(index + 1).trim();

            if (img) {
                firstColorImage = img;
                break;
            }
        }
    }

    document.getElementById("popupProductImage").src =
        firstColorImage;
    /* -----------------------------
       COLOR IMAGE MAP
    ------------------------------ */

    let colorImageMap = {};

    if (btn.dataset.colorImages) {

        btn.dataset.colorImages
            .split(",")
            .forEach(item => {

                const parts = item.split(":");

                if (parts.length >= 2) {

                    colorImageMap[
                        parts[0].trim().toLowerCase()
                    ] = parts.slice(1).join(":").trim();

                }

            });

    }

    /* -----------------------------
       COLORS
    ------------------------------ */

    const colorsDiv =
        document.getElementById("popupColors");

    colorsDiv.innerHTML = "";

    (btn.dataset.colors || "")
        .split(",")
        .forEach(color => {

            color = color.trim();

            if (!color) return;

            const img =
                colorImageMap[color.toLowerCase()] ||
                wishlistDefaultImage;

            colorsDiv.innerHTML += `

        <span class="variant-option"
              data-color-img="${img}">

            <img src="${img}"
                 style="
                    width:40px;
                    height:40px;
                    object-fit:cover;
                    border-radius:8px;
                    margin-right:8px;
                 ">

            <span>${color}</span>

        </span>

        `;

        });

    /* -----------------------------
       SIZES
    ------------------------------ */

    const sizesDiv =
        document.getElementById("popupSizes");

    sizesDiv.innerHTML = "";

    (btn.dataset.sizes || "")
        .split(",")
        .forEach(size => {

            size = size.trim();

            if (!size) return;

            sizesDiv.innerHTML += `
    <span class="variant-option">
        ${size}
    </span>
`;

        });

    document.getElementById("variantPopup").style.display = "flex";

});


/* =========================================
SELECT COLOR / SIZE
========================================= */

document.addEventListener("click", function (e) {

    const option =
        e.target.closest(".variant-option");

    if (!option) return;

    const parent =
        option.parentElement;

    parent
        .querySelectorAll(".variant-option")
        .forEach(x => x.classList.remove("active"));

    option.classList.add("active");

    // Color selected
    if (parent.id === "popupColors") {
        document.getElementById("popupProductImage").src =
            option.dataset.colorImg;
    }

    // Size selected
    if (parent.id === "popupColors") {
    }

});

function closeVariantPopup() {

    document.getElementById(
        "variantPopup"
    ).style.display = "none";

}