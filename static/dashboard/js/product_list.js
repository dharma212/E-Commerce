// ========================================
// TOAST MESSAGE
// ========================================

// ================= TOAST =================
function showToast(message, type = "success") {

    let toastContainer =
        document.getElementById("toastContainer");

    // AUTO CREATE CONTAINER
    if(!toastContainer){

        toastContainer = document.createElement("div");

        toastContainer.id = "toastContainer";

        toastContainer.style.position = "fixed";
        toastContainer.style.top = "20px";
        toastContainer.style.right = "20px";
        toastContainer.style.zIndex = "999999";

        document.body.appendChild(toastContainer);

    }

    const toast = document.createElement("div");

    toast.className = "custom-toast";

    toast.style.minWidth = "250px";
    toast.style.marginBottom = "10px";
    toast.style.padding = "12px 18px";
    toast.style.borderRadius = "10px";
    toast.style.color = "#fff";
    toast.style.fontWeight = "600";
    toast.style.boxShadow = "0 4px 15px rgba(0,0,0,0.2)";
    toast.style.opacity = "0";
    toast.style.transition = "0.3s";

    if(type === "success"){

        toast.style.background = "#198754";

    }else{

        toast.style.background = "#dc3545";

    }

    toast.innerText = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {

        toast.style.opacity = "1";

    }, 100);

    setTimeout(() => {

        toast.style.opacity = "0";

        setTimeout(() => {

            toast.remove();

        }, 300);

    }, 3000);

}

// ========================================
// CSRF TOKEN
// ========================================

function getCSRFToken(){

    let cookieValue = null;

    const cookies = document.cookie.split(';');

    for(let i = 0; i < cookies.length; i++){

        const cookie = cookies[i].trim();

        if(cookie.startsWith('csrftoken=')){

            cookieValue = cookie.substring('csrftoken='.length);

            break;
        }
    }

    return cookieValue;
}


// ========================================
// LOAD PRODUCTS
// ========================================

function loadProducts(){

    fetch('/api/products/')

    .then(res => {

        if(!res.ok){

            throw new Error("Failed to load products");
        }

        return res.json();

    })

    .then(data => {

        let tbody = '';

        data.forEach((item, index) => {

            let imageUrl = '';

            if(item.images && item.images.length > 0){

                imageUrl = item.images[0].image;
            }

            tbody += `

            <tr>

                <td>${index + 1}</td>

                <td>

                    ${
                        imageUrl

                        ?

                        `<img src="${imageUrl}"
                              class="product-img"
                              onclick='openImageGallery(${JSON.stringify(item.images)})'>`

                        :

                        `<div class="no-img-box">
                            <i class="bi bi-image"></i>
                        </div>`
                    }

                </td>

                <td class="product-name">

                    <div class="product-title">

                        ${
                            item.name && item.name.length > 35

                            ?

                            item.name.substring(0, 35) + '...'

                            :

                            item.name
                        }

                    </div>

                    ${
                        item.discount > 0

                        ?

                        `<span class="discount-badge">
                            ${item.discount_percent}% OFF
                        </span>`

                        : ''
                    }

                </td>

                <td>${item.category_name || 'N/A'}</td>

                <td>${item.type_name || 'N/A'}</td>

                <td>

                    <span class="color-badge"
                          style="background:${item.color_name ? item.color_name.toLowerCase() : '#555'}">

                        ${item.color_name || 'N/A'}

                    </span>

                </td>

                <td>

                    <span class="size-badge">

                        ${item.size_name || 'N/A'}

                    </span>

                </td>

                <td class="price">

                    <div class="final-price">

                        ₹ ${item.final_price || 0}

                    </div>

                    ${
                        item.discount > 0

                        ?

                        `<div class="mrp-price">
                            <del>₹ ${item.mrp}</del>
                        </div>`

                        : ''
                    }

                </td>

                <td>

                    ${
                        item.discount > 0

                        ?

                        `<span class="green-text">
                            ${item.discount_percent}% OFF
                        </span>`

                        :

                        `<span class="gray-text">
                            No Discount
                        </span>`
                    }

                </td>

                <td>

                    ${
                        item.stock > 0

                        ?

                        `<span class="stock-badge stock-in">
                            ${item.stock} In Stock
                        </span>`

                        :

                        `<span class="stock-badge stock-out">
                            Out Of Stock
                        </span>`
                    }

                </td>

                <td>

                    <div class="action-wrapper">

                        <a href="/dashboard/add-product/?edit=${item.id}"
                           class="icon-btn edit-btn">

                            <i class="bi bi-pencil-fill"></i>

                        </a>

                        <button class="icon-btn delete-btn"
                                data-id="${item.id}">

                            <i class="bi bi-trash-fill"></i>

                        </button>

                    </div>

                </td>

            </tr>

            `;
        });

        // ==========================
        // ADD HTML
        // ==========================

        $('#productTable tbody').html(tbody);

        // ==========================
        // DESTROY OLD TABLE
        // ==========================

        if($.fn.DataTable.isDataTable('#productTable')){

            $('#productTable').DataTable().destroy();
        }

        // ==========================
        // INIT DATATABLE
        // ==========================

        $('#productTable').DataTable({

            destroy:true,

            pageLength:10,

            ordering:true,

            responsive:false,

            autoWidth:false,

            scrollX:false,

            columnDefs:[

                {
                    targets:-1,
                    orderable:false,
                    searchable:false
                }

            ],

            language:{

                lengthMenu:
                    "Show _MENU_ entries",

                zeroRecords:
                    "No matching products found",

                info:
                    "Showing _START_ to _END_ of _TOTAL_ products",

                infoEmpty:
                    "No products available",

                search:"",

                searchPlaceholder:
                    "Search products...",

                paginate:{

                    previous:
                        "<i class='bi bi-chevron-left'></i>",

                    next:
                        "<i class='bi bi-chevron-right'></i>"
                }
            }
        });

        // ==========================
        // DELETE BUTTON
        // ==========================

        $('.delete-btn').off('click').on('click', function(){

            let id = $(this).data('id');

            deleteProduct(id);

        });

    })

    // .catch(error => {

    //     console.log(error);

    //     showToast(
    //         "Failed to load products",
    //         "error"
    //     );

    // });

}


// ================================
// PAGE LOAD
// ================================

document.addEventListener("DOMContentLoaded", function(){

    loadProducts();

});


// ========================================
// DELETE PRODUCT
// ========================================

function deleteProduct(id){

    fetch(`/api/products/${id}/delete/`, {

        method:"DELETE",

        headers:{

            "X-CSRFToken": getCSRFToken(),
            "Content-Type":"application/json"

        }

    })

    .then(res => {

        if(!res.ok){

            throw new Error("Delete failed");
        }

        return res.json();
    })

    .then(data => {

        showToast(data.message, "success");

        loadProducts();

    })

    .catch(error => {

        console.log(error);

        showToast(
    "Failed to delete product",
    "error"
);

    });
}


// ========================================
// CLOSE MODAL
// ========================================

const closeBtn = document.querySelector(".close-btn");

if(closeBtn){

    closeBtn.onclick = function(){

        const modal = document.getElementById("imageModal");

        if(modal){

            modal.style.display = "none";
        }
    };
}


// ========================================
// CLOSE MODAL ON OUTSIDE CLICK
// ========================================

window.onclick = function(event){

    const modal = document.getElementById("imageModal");

    if(event.target === modal){

        modal.style.display = "none";
    }
};


// ========================================
// IMAGE GALLERY
// ========================================

function openImageGallery(images){

    let modal = document.getElementById("imageModal");

    let mainImg = document.getElementById("modalMainImg");

    let thumbContainer = document.getElementById("thumbnailContainer");

    modal.style.display = "block";

    thumbContainer.innerHTML = "";

    if(!images || images.length === 0){
        return;
    }

    // FIRST IMAGE
    mainImg.src = images[0].image;

    images.forEach((imgObj, index) => {

        let thumb = document.createElement("img");

        thumb.src = imgObj.image;

        thumb.className = "thumb-img";

        if(index === 0){

            thumb.classList.add("active");
        }

        thumb.onclick = () => {

            mainImg.src = imgObj.image;

            document.querySelectorAll(".thumb-img")
            .forEach(el => el.classList.remove("active"));

            thumb.classList.add("active");
        };

        thumbContainer.appendChild(thumb);
    });
}


// ========================================
// INITIAL LOAD
// ========================================

document.addEventListener("DOMContentLoaded", function(){

    loadProducts();

});
