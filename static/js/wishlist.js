function getCSRFToken() {

    return document.querySelector(
        '[name=csrfmiddlewaretoken]'
    ).value;

}

// ======================================
// WISHLIST FUNCTION
// ======================================

function toggleWishlist(productId, currentButton, removeCard=false) {

    fetch("/api/wishlist/", {

        method: "POST",

        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded",
        },

        body: new URLSearchParams({
            product_id: productId
        })

    })

    .then(response => response.json())

    .then(data => {

        let icon = currentButton.querySelector("i");

        // =========================
        // ADD
        // =========================
        if (data.status === "added") {

            currentButton.classList.add("active");

            if (icon) {

                icon.classList.remove("far");

                icon.classList.add("fas");

            }

        }

        // =========================
        // REMOVE
        // =========================
        else if (data.status === "removed") {

            currentButton.classList.remove("active");

            if (icon) {

                icon.classList.remove("fas");

                icon.classList.add("far");

            }

            // REMOVE CARD
            if (removeCard) {

                const card = document.querySelector(
                    `.wishlist-card-${productId}`
                );

                if (card) {

                    card.remove();

                }

            }

        }

        // =========================
        // UPDATE WISHLIST COUNT
        // =========================
        const wishlistCount = document.getElementById(
            "wishlist-count"
        );

        if (wishlistCount) {

            wishlistCount.innerText =
                data.wishlist_count;

        }

    })

    .catch(error => {

        console.log(error);

    });

}

// ======================================
// INDEX PAGE BUTTONS
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".wishlist-btn")
    .forEach(button => {

        button.addEventListener("click", function () {

            toggleWishlist(
                this.dataset.productId,
                this
            );

        });

    });

    // ======================================
    // REMOVE BUTTONS
    // ======================================

    document.querySelectorAll(".remove-wishlist-btn")
    .forEach(button => {

        button.addEventListener("click", function () {

            toggleWishlist(
                this.dataset.productId,
                this,
                true
            );

        });

    });

});
