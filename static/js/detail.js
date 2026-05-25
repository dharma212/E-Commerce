// ======================================
// PRODUCT IMAGE GALLERY
// ======================================

const thumbnails = document.querySelectorAll(".small-product-image");

const mainImage = document.getElementById(
    "mainProductImage"
);

let currentImageIndex = 0;

let autoSlide;


// CHANGE IMAGE
function changeMainImage(element, index){

    mainImage.src = element.src;

    thumbnails.forEach(img => {

        img.classList.remove(
            "active-thumb"
        );

    });

    element.classList.add(
        "active-thumb"
    );

    currentImageIndex = index;
}


// UPDATE IMAGE
function updateMainImage(){

    if(!thumbnails.length) return;

    const currentThumb =
    thumbnails[currentImageIndex];

    mainImage.src = currentThumb.src;

    thumbnails.forEach(img => {

        img.classList.remove(
            "active-thumb"
        );

    });

    currentThumb.classList.add(
        "active-thumb"
    );

}


// NEXT IMAGE
function nextImage(){

    currentImageIndex++;

    if(currentImageIndex >= thumbnails.length){

        currentImageIndex = 0;

    }

    updateMainImage();

}


// PREVIOUS IMAGE
function previousImage(){

    currentImageIndex--;

    if(currentImageIndex < 0){

        currentImageIndex =
        thumbnails.length - 1;

    }

    updateMainImage();

}


// AUTO SLIDE
function startAutoSlide(){

    autoSlide = setInterval(() => {

        if(thumbnails.length > 1){

            nextImage();

        }

    }, 3000);

}


// STOP AUTO SLIDE
function stopAutoSlide(){

    clearInterval(autoSlide);

}


// START GALLERY
const imageBox =
document.querySelector(".main-image-box");

if(imageBox){

    startAutoSlide();

    imageBox.addEventListener(
        "mouseenter",
        stopAutoSlide
    );

    imageBox.addEventListener(
        "mouseleave",
        startAutoSlide
    );

}



// ======================================
// CSRF TOKEN
// ======================================

function getCSRFToken(){

    const csrf =
    document.querySelector(
        "[name=csrfmiddlewaretoken]"
    );

    if(csrf){
        return csrf.value;
    }

    return "";
}



// ======================================
// QUANTITY
// ======================================

const quantityInput =
document.querySelector(
    ".details-quantity-input"
);

const plusBtn =
document.querySelector(
    ".btn-plus"
);

const minusBtn =
document.querySelector(
    ".btn-minus"
);

// PRODUCT ID
const mainCartBtn =
document.querySelector(
    ".add-to-cart"
);

let mainProductId = null;

if(mainCartBtn){

    mainProductId =
    mainCartBtn.dataset.id;

}


// STORAGE KEY
const storageKey =
`product_qty_${mainProductId}`;



// LOAD SAVED QTY
if(quantityInput){

    const savedQty =
    localStorage.getItem(storageKey);

    if(savedQty){

        quantityInput.value =
        savedQty;

    }

}



// UPDATE BUTTON STATE
function updateQuantityButtons(){

    if(!quantityInput) return;

    let qty =
    parseInt(quantityInput.value);

    let maxStock =
    parseInt(
        quantityInput.dataset.stock
    );

    // PLUS BUTTON
    if(qty >= maxStock){

        plusBtn.disabled = true;

    }
    else{

        plusBtn.disabled = false;

    }

    // MINUS BUTTON
    if(qty <= 1){

        minusBtn.disabled = true;

    }
    else{

        minusBtn.disabled = false;

    }

}



// PLUS
if(plusBtn){

    plusBtn.addEventListener(
        "click",
        function(){

            let qty =
            parseInt(quantityInput.value);

            const maxStock =
            parseInt(
                quantityInput.dataset.stock
            );

            if(qty < maxStock){

                qty++;

                quantityInput.value = qty;

                localStorage.setItem(
                    storageKey,
                    qty
                );

                updateQuantityButtons();

            }

        }
    );

}



// MINUS
if(minusBtn){

    minusBtn.addEventListener(
        "click",
        function(){

            let qty =
            parseInt(quantityInput.value);

            if(qty > 1){

                qty--;

                quantityInput.value = qty;

                localStorage.setItem(
                    storageKey,
                    qty
                );

                updateQuantityButtons();

            }

        }
    );

}



// MANUAL INPUT
if(quantityInput){

    quantityInput.addEventListener(
        "input",
        function(){

            let qty =
            parseInt(this.value);

            const maxStock =
            parseInt(
                this.dataset.stock
            );

            if(isNaN(qty) || qty < 1){

                qty = 1;

            }

            if(qty > maxStock){

                qty = maxStock;

            }

            this.value = qty;

            localStorage.setItem(
                storageKey,
                qty
            );

            updateQuantityButtons();

        }
    );

}


updateQuantityButtons();
