// ================= GLOBAL VARIABLES =================
let selectedColor = "";
let selectedSize = "";
let currentVisibleIndex = 0; 
let actionType = "";
let currentProductId = "";

// ================= IMAGE GALLERY LOGIC =================


function updateMainImageFromVisible(index) {
    let visibleThumbs = Array.from(document.querySelectorAll(".thumb-wrapper"))
                             .filter(wrapper => wrapper.style.display !== "none");

    if (visibleThumbs.length === 0) return;

    if (visibleThumbs.length === 1) {
        index = 0;
    } else {
        if (index >= visibleThumbs.length) index = 0;
        if (index < 0) index = visibleThumbs.length - 1;
    }

    currentVisibleIndex = index;

    let targetImg = visibleThumbs[currentVisibleIndex].querySelector("img");
    document.getElementById("mainProductImage").src = targetImg.src;

    document.querySelectorAll(".small-product-image").forEach(t => t.classList.remove("active-thumb"));
    targetImg.classList.add("active-thumb");
}

function nextImage() {
    updateMainImageFromVisible(currentVisibleIndex + 1);
}

function previousImage() {
    updateMainImageFromVisible(currentVisibleIndex - 1);
}

function changeMainImage(element) {
    document.getElementById("mainProductImage").src = element.src;
    document.querySelectorAll(".small-product-image").forEach(thumb => thumb.classList.remove("active-thumb"));
    element.classList.add("active-thumb");
    
    let visibleThumbs = Array.from(document.querySelectorAll(".thumb-wrapper"))
                             .filter(wrapper => wrapper.style.display !== "none");
    currentVisibleIndex = visibleThumbs.findIndex(wrapper => wrapper.contains(element));
}

// ================= COLOR & SIZE SELECTION =================

document.addEventListener("DOMContentLoaded", function() {
    
    // COLOR SELECTION
    document.querySelectorAll(".color-box").forEach(box => {
        box.addEventListener("click", function() {
            document.querySelectorAll(".color-box").forEach(c => c.classList.remove("active"));
            this.classList.add("active");

            selectedColor = this.dataset.color.trim().toLowerCase();
            currentVisibleIndex = 0; 

            let foundFirstImage = false;
            document.querySelectorAll(".thumb-wrapper").forEach(wrapper => {
                let imgColor = wrapper.getAttribute("data-thumb-color");

                if (imgColor === selectedColor) {
                    wrapper.style.display = "block";
                    if (!foundFirstImage) {
                        updateMainImageFromVisible(0);
                        foundFirstImage = true;
                    }
                } else {
                    wrapper.style.display = "none";
                }
            });
        });
    });

    // SIZE SELECTION
    document.querySelectorAll(".size-badge").forEach(box => {
        box.addEventListener("click", function() {
            if(this.classList.contains("active")){
                this.classList.remove("active");
                selectedSize = "";
                return;
            }
            document.querySelectorAll(".size-badge").forEach(s => s.classList.remove("active"));
            this.classList.add("active");
            selectedSize = this.dataset.size;
        });
    });

    // QUANTITY LOGIC
    $('.btn-plus').on('click', function() {
        let input = $('.details-quantity-input');
        let currentVal = parseInt(input.val());
        let maxStock = parseInt(input.data('stock'));
        if (currentVal < maxStock) {
            input.val(currentVal + 1);
            $('.btn-minus').prop('disabled', false);
        }
        if (parseInt(input.val()) >= maxStock) { $(this).prop('disabled', true); }
    });

    $('.btn-minus').on('click', function() {
        let input = $('.details-quantity-input');
        let currentVal = parseInt(input.val());
        if (currentVal > 1) {
            input.val(currentVal - 1);
            $('.btn-plus').prop('disabled', false);
        }
        if (parseInt(input.val()) <= 1) { $(this).prop('disabled', true); }
    });
});

// ================= RATINGS POPOVER =================

const popover = document.getElementById("ratingModal");
const openTxt = document.getElementById("openRatingPopup");
const summaryView = document.getElementById("summary-view");
const reviewsListView = document.getElementById("popover-reviews-list");

if(openTxt){
    openTxt.addEventListener("click", function(e){
        e.stopPropagation();
        popover.classList.toggle("show");
        if(popover.classList.contains("show")){
            summaryView.style.display = "block";
            reviewsListView.style.display = "none";
            document.querySelectorAll(".progress-bar").forEach(bar => {
                const originalWidth = bar.style.width;
                bar.style.width = "0%";
                setTimeout(() => {
                    bar.style.transition = "width 1s ease";
                    bar.style.width = originalWidth;
                }, 100);
            });
        }
    });
}

$("#show-popover-reviews").click(function(){ $("#summary-view").hide(); $("#popover-reviews-list").show(); });
$("#back-to-summary").click(function(){ $("#popover-reviews-list").hide(); $("#summary-view").show(); });
$(".rating-close-btn").click(function(){ 
    document.getElementById("ratingModal").classList.remove("show"); 
});

document.addEventListener("click", function(e) {
    const popoverBox = document.getElementById("ratingModal");
    const triggerTxt = document.getElementById("openRatingPopup");
    
    if (popoverBox && popoverBox.classList.contains("show")) {
        if (!popoverBox.contains(e.target) && e.target !== triggerTxt && !triggerTxt.contains(e.target)) {
            popoverBox.classList.remove("show");
        }
    }
});

// ================= VARIANT MODAL & AJAX =================

function checkVariantSelection(){
    let hasColor = $(".popup-color-box").length > 0;
    let hasSize = $(".popup-size-box").length > 0;
    let colorOk = !hasColor || selectedPopupColor;
    let sizeOk = !hasSize || selectedPopupSize;
    $("#continueVariantBtn").prop("disabled", !(colorOk && sizeOk));
}

$(".buy-now, .add-to-cart").click(function(e){
    e.preventDefault();
    currentProductId = $(this).data("id");
    actionType = $(this).hasClass("buy-now") ? "buy" : "cart";
    
    let hasColor = $(".color-box").length > 0;
    let hasSize = $(".size-badge").length > 0;
    
    if((!hasColor || selectedColor) && (!hasSize || selectedSize)){
        handleFinalAction(); 
        return;
    }

    $("#variantModal").fadeIn();
});
$(".close-variant").click(function(){
    $("#variantModal").fadeOut();
});

$(window).click(function(event) {
    if (event.target == document.getElementById("variantModal")) {
        $("#variantModal").fadeOut();
    }
});
$(".popup-color-box").click(function(){
    $(".popup-color-box").removeClass("active");
    $(this).addClass("active");
    selectedPopupColor = $(this).data("color");
    selectedColor = selectedPopupColor;
    $('.color-box[data-color="' + selectedColor + '"]').trigger("click");
    checkVariantSelection();
});

$(".popup-size-box").click(function(){
    $(".popup-size-box").removeClass("active");
    $(this).addClass("active");
    
    selectedPopupSize = $(this).attr("data-size") ? $(this).attr("data-size").trim() : $(this).text().trim();
    selectedSize = selectedPopupSize;
    
    $('.size-badge').removeClass("active");
    $('.size-badge[data-size="' + selectedSize + '"]').addClass("active");
    
    popupCheckSelection();
});
$("#continueVariantBtn").click(function(){ handleFinalAction(); });

function handleFinalAction(){

    if(actionType == "cart"){

        $("#variantModal").fadeOut();

        const cartBtn =
            document.querySelector(".add-to-cart");

        if(cartBtn){

            cartBtn.click();

        }

    }else{

        let qty =
            $(".details-quantity-input").val() || 1;

        let checkoutUrl =
            "/checkout/?buy_now=" +
            currentProductId +
            "&qty=" + qty +
            "&color=" + encodeURIComponent(selectedColor) +
            "&size=" + encodeURIComponent(selectedSize);

        window.location.href = checkoutUrl;
    }
}
function popupCheckSelection() {
    let hasColor = $(".popup-color-box").length > 0;
    let hasSize = $(".popup-size-box").length > 0;
    
    let colorOk = !hasColor || selectedColor;
    let sizeOk = !hasSize || selectedSize;
    
    $("#continueVariantBtn").prop("disabled", !(colorOk && sizeOk));
}
document.addEventListener("DOMContentLoaded", function () {

    const btn = document.querySelector(".view-more-name");

    if(btn){

        btn.addEventListener("click", function(){

            const shortName = document.querySelector(".short-name");
            const fullName = document.querySelector(".full-name");

            if(fullName.style.display === "none"){

                fullName.style.display = "inline";
                shortName.style.display = "none";
                btn.innerText = " View Less";

            }else{

                fullName.style.display = "none";
                shortName.style.display = "inline";
                btn.innerText = " View More";

            }
        });

    }

});
// ================= THUMBNAIL ONLY SCROLL LOGIC =================
function scrollThumbnails(direction) {
    const track = document.getElementById('thumbScrollTrack');
    if (!track) return;

    const scrollAmount = 190; 
    
    if (direction === 'left') {
        track.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else if (direction === 'right') {
        track.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}