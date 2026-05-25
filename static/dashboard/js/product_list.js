fetch('/api/products/')
.then(res => res.json())
.then(data => {

    let tbody = '';

    data.forEach((item, index) => {

        let imageUrl = '';

        // FIRST IMAGE
        if(item.images && item.images.length > 0){

            imageUrl = item.images[0].image;

        }

        tbody += `
        <tr>

            <!-- ID -->
            <td>
                ${index + 1}
            </td>

            <!-- IMAGE -->
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

            <!-- PRODUCT -->
            <td class="product-name">

                <div class="product-title">

                    ${
                        item.name.length > 40

                        ?

                        item.name.substring(0, 40) + '...'

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

            <!-- CATEGORY -->
            <td>

                ${item.category_name}

            </td>

            <!-- TYPE -->
            <td>

                ${item.type_name}

            </td>

            <!-- COLOR -->
            <td>

                <span class="color-badge"
                      style="background:${item.color_name?.toLowerCase() || '#333'}">

                    ${item.color_name || 'N/A'}

                </span>

            </td>

            <!-- SIZE -->
            <td>

                <span class="size-badge">

                    ${item.size_name || 'N/A'}

                </span>

            </td>

            <!-- PRICE -->
            <td class="price">

                ${
                    item.discount > 0

                    ?

                    `
                        <div class="final-price">

                            ₹ ${item.final_price}

                        </div>

                        <div class="mrp-price">

                            <del>₹ ${item.mrp}</del>

                        </div>
                    `

                    :

                    `<div class="final-price">

                        ₹ ${item.price}

                    </div>`
                }

            </td>

            <!-- DISCOUNT -->
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

            <!-- STOCK -->
            <td>

                ${item.stock}

            </td>

            <!-- ACTION -->
            <td>

                <button class="btn btn-sm btn-primary">

                    <i class="bi bi-pencil"></i>

                </button>

                <button class="btn btn-sm btn-danger">

                    <i class="bi bi-trash"></i>

                </button>

            </td>

        </tr>
        `;
    });

    $('#productTable tbody').html(tbody);

    // DATATABLE
    if($.fn.DataTable){

        $('#productTable').DataTable({

            destroy:true,
            pageLength:5,
            lengthChange:false,
            info:false

        });

    }

});


// CLOSE MODAL
const closeBtn = document.querySelector(".close-btn");

if(closeBtn){

    closeBtn.onclick = function(){

        const modal = document.getElementById("imageModal");

        if(modal){

            modal.style.display = "none";

        }

    };

}


// IMAGE GALLERY
function openImageGallery(images){

    let modal = document.getElementById("imageModal");
    let mainImg = document.getElementById("modalMainImg");
    let thumbContainer = document.getElementById("thumbnailContainer");

    modal.style.display = "block";

    thumbContainer.innerHTML = "";

    if(!images || images.length === 0) return;

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