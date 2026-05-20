
fetch('/api/products/')
.then(res => res.json())
.then(data => {


    let tbody = '';

    data.forEach((item, index) => {

        let imageUrl = '';

        if(item.images && item.images.length > 0){
            imageUrl = 'http://127.0.0.1:8000' + item.images[0].image;
        }

        tbody += `
        <tr>

            <td>${index + 1}</td>

            <!-- IMAGE -->
            <td>
                ${
                    imageUrl 
                    ? `<img src="${imageUrl}" class="product-img" onclick='openImageGallery(${JSON.stringify(item.images)})'>`
                    : `<span class="no-img">No Image</span>`
                }
            </td>

            <!-- PRODUCT NAME -->
            <td class="product-name">
                ${item.name}

                ${
                    item.discount > 0
                    ? `<span style="
                        background:#28a745;
                        color:#fff;
                        font-size:10px;
                        padding:2px 6px;
                        border-radius:4px;
                        margin-left:5px;
                    ">${item.discount_percent}% OFF</span>`
                    : ''
                }
            </td>

            <td>${item.category_name}</td>
            <td>${item.type_name}</td>
            <!-- COLOR -->
            <td>
                <span style="
                    background:${item.color_name?.toLowerCase() || '#333'};
                    color:white;
                    padding:4px 10px;
                    border-radius:20px;
                    font-size:12px;
                    font-weight:600;
                ">
                    ${item.color_name || 'N/A'}
                </span>
            </td>

            <!-- SIZE -->
            <td>
                <span style="
                    background:#f1f1f1;
                    color:#333;
                    padding:4px 10px;
                    border-radius:6px;
                    font-size:12px;
                    font-weight:600;
                ">
                    ${item.size_name || 'N/A'}
                </span>
            </td>

            <!-- PRICE COLUMN -->
            <td class="price">

                ${
                    item.discount > 0 
                    ? `
                        <div>₹ ${item.final_price}</div>
                        <div style="font-size:12px;color:#888;">
                            <del>₹ ${item.mrp}</del>
                        </div>
                      `
                    : `₹ ${item.price}`
                }

            </td>

            <!-- DISCOUNT COLUMN -->
            <td>

                ${
                    item.discount > 0 
                    ? `<span style="color:#28a745;font-weight:600;">
                        ${item.discount_percent}% OFF
                       </span>`
                    : `<span style="color:#aaa;">No Discount</span>`
                }

            </td>

            <td>${item.stock}</td>

            <td>
                <button class="btn btn-sm btn-primary"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-danger"><i class="bi bi-trash"></i></button>
            </td>

        </tr>
        `;
    });

    $('#productTable tbody').html(tbody);
    if ($.fn.DataTable) {
        $('#productTable').DataTable({
            pageLength: 5,
            lengthChange: false,
            info: false
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

    let firstImg = 'http://127.0.0.1:8000' + images[0].image;
    mainImg.src = firstImg;

    images.forEach((imgObj, index) => {

        let imgUrl = 'http://127.0.0.1:8000' + imgObj.image;

        let thumb = document.createElement("img");
        thumb.src = imgUrl;
        thumb.className = "thumb-img";

        if(index === 0){
            thumb.classList.add("active");
        }

        thumb.onclick = () => {
            mainImg.src = imgUrl;
            document.querySelectorAll(".thumb-img").forEach(el => el.classList.remove("active"));
            thumb.classList.add("active");
        };

        thumbContainer.appendChild(thumb);
    });
}