const thumbnails = document.querySelectorAll(".small-product-image");
const mainImage = document.getElementById("mainProductImage");

let currentImageIndex = 0;
let autoSlide;

/* CHANGE MAIN IMAGE */
function changeMainImage(element, index){

    mainImage.src = element.src;

    thumbnails.forEach(img=>{
        img.classList.remove("active-thumb");
    });

    element.classList.add("active-thumb");

    currentImageIndex = index;
}

/* UPDATE IMAGE */
function updateMainImage(){

    const currentThumb = thumbnails[currentImageIndex];

    if(currentThumb){

        mainImage.src = currentThumb.src;

        thumbnails.forEach(img=>{
            img.classList.remove("active-thumb");
        });

        currentThumb.classList.add("active-thumb");
    }
}

/* NEXT IMAGE */
function nextImage(){

    currentImageIndex++;

    if(currentImageIndex >= thumbnails.length){
        currentImageIndex = 0;
    }

    updateMainImage();
}

/* PREVIOUS IMAGE */
function previousImage(){

    currentImageIndex--;

    if(currentImageIndex < 0){
        currentImageIndex = thumbnails.length - 1;
    }

    updateMainImage();
}

/* AUTO SLIDE */
function startAutoSlide(){

    autoSlide = setInterval(()=>{

        if(thumbnails.length > 1){
            nextImage();
        }

    }, 3000);
}

/* STOP AUTO SLIDE */
function stopAutoSlide(){
    clearInterval(autoSlide);
}

/* START */
startAutoSlide();

/* PAUSE ON HOVER */
document.querySelector(".main-image-box").addEventListener("mouseenter", ()=>{
    stopAutoSlide();
});

document.querySelector(".main-image-box").addEventListener("mouseleave", ()=>{
    startAutoSlide();
});


// ======================================
// CSRF TOKEN
// ======================================

function getCSRFToken(){

    return document.querySelector(
        '[name=csrfmiddlewaretoken]'
    ).value;

}


// =====================================
// WISHLIST
// =====================================

document.querySelectorAll(
    ".wishlist-btn"
).forEach(button => {

    button.addEventListener(
        "click",
        function () {

            const btn = this;

            const productId =
            btn.dataset.productId;

            fetch(`/wishlist-toggle/${productId}/`, {

                method: "POST",

                headers: {

                    "Content-Type":
                    "application/json",

                    "X-CSRFToken":
                    getCSRFToken()

                }

            })

            .then(response => response.json())

            .then(data => {

                const icon =
                btn.querySelector("i");



                if(data.status === "added"){

                    btn.classList.remove(
                        "btn-outline-dark"
                    );

                    btn.classList.add(
                        "btn-danger"
                    );

                    icon.classList.remove(
                        "far"
                    );

                    icon.classList.add(
                        "fas"
                    );



                    Toastify({

                        text: "Added To Wishlist",

                        duration: 2000,

                        gravity: "top",

                        position: "right",

                        backgroundColor: "#28a745",

                    }).showToast();

                }

                else{

                    btn.classList.remove(
                        "btn-danger"
                    );

                    btn.classList.add(
                        "btn-outline-dark"
                    );

                    icon.classList.remove(
                        "fas"
                    );

                    icon.classList.add(
                        "far"
                    );



                    Toastify({

                        text: "Removed From Wishlist",

                        duration: 2000,

                        gravity: "top",

                        position: "right",

                        backgroundColor: "#dc3545",

                    }).showToast();

                }

            });

        }
    );

});
