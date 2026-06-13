// ================= GLOBAL =================
let selectedImages = [];
let isEditMode = false;
let editProductId = null;

// ================= TOAST =================
function getToastContainer() {

    let container =
        document.getElementById("globalToastContainer");

    if (!container) {

        container =
            document.createElement("div");

        container.id = "globalToastContainer";

        container.style.position = "fixed";
        container.style.top = "20px";
        container.style.right = "20px";
        container.style.zIndex = "999999";

        document.body.appendChild(container);
    }

    return container;
}

function showToast(
    message,
    type = "success",
    duration = 3000
) {

    const container =
        getToastContainer();

    if(!container){
        return;
    }

    const toast =
        document.createElement("div");

    toast.style.minWidth = "260px";
    toast.style.marginBottom = "10px";
    toast.style.padding = "14px 16px";
    toast.style.borderRadius = "10px";
    toast.style.color = "#fff";
    toast.style.fontSize = "14px";
    toast.style.display = "flex";
    toast.style.alignItems = "center";
    toast.style.gap = "10px";
    toast.style.boxShadow =
        "0 8px 20px rgba(0,0,0,0.2)";
    toast.style.opacity = "0";
    toast.style.transform =
        "translateX(100%)";
    toast.style.transition =
        "all 0.4s ease";

    let icon =
        `<i class="bi bi-check-circle-fill"></i>`;

    if(type === "error"){

        icon =
            `<i class="bi bi-x-circle-fill"></i>`;
    }

    if(type === "warning"){

        icon =
            `<i class="bi bi-exclamation-triangle-fill"></i>`;
    }

    if(type === "success"){

        toast.style.background = "#4CAF50";

    }else if(type === "error"){

        toast.style.background = "#e74c3c";

    }else if(type === "warning"){

        toast.style.background = "#f39c12";

    }else{

        toast.style.background = "#333";
    }

    toast.innerHTML =
        `${icon} <span>${message}</span>`;

    container.appendChild(toast);

    requestAnimationFrame(() => {

        toast.style.opacity = "1";
        toast.style.transform =
            "translateX(0)";
    });

    setTimeout(() => {

        toast.style.opacity = "0";

        toast.style.transform =
            "translateX(100%)";

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, duration);
}

// ================= CSRF =================
function getCSRFToken() {

    let name = "csrftoken=";

    let cookies =
        document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {

        let c =
            cookies[i].trim();

        if (c.startsWith(name)) {

            return c.substring(
                name.length,
                c.length
            );
        }
    }

    return "";
}

// ================= ERROR =================
function clearErrors() {

    document.querySelectorAll(".error-text")
    .forEach(el => {

        el.innerText = "";
    });

    document.querySelectorAll(".form-control")
    .forEach(el => {

        el.classList.remove("input-error");
    });
}

function showError(inputId, message) {

    let errorEl =
        document.getElementById(
            `error-${inputId}`
        );

    if (errorEl) {

        errorEl.innerText = message;
    }

    let inputEl =
        document.getElementById(inputId);

    if (inputEl) {

        inputEl.classList.add("input-error");
    }
}

// ================= SEARCH =================
function setupSearch(
    inputId,
    resultId,
    hiddenId
) {

    const input =
        document.getElementById(inputId);

    const resultBox =
        document.getElementById(resultId);

    const hiddenInput =
        document.getElementById(hiddenId);

    if(
        !input ||
        !resultBox ||
        !hiddenInput
    ){
        return;
    }

    // ================= FOCUS =================
    input.addEventListener("focus", function(){

        resultBox.style.display = "block";

        const items =
            resultBox.querySelectorAll(".search-item");

        items.forEach(item => {

            item.style.display = "block";
        });

    });

    // ================= SEARCH =================
    input.addEventListener("input", function(){

        const value =
            this.value.toLowerCase().trim();

        const items =
            resultBox.querySelectorAll(".search-item");

        hiddenInput.value = "";

        resultBox.style.display = "block";

        items.forEach(item => {

            const name =
                (item.dataset.name || "")
                .toLowerCase();

            if(name.includes(value)){

                item.style.display = "block";

            }else{

                item.style.display = "none";
            }

        });

    });

    // ================= CLICK =================
    resultBox.addEventListener("click", function(e){

        const item =
            e.target.closest(".search-item");

// ================= SELECT =================
if(item){

    const selectedName =
        item.innerText.trim();

    const selectedId =
        item.dataset.id;

    // CURRENT VALUES
    let currentNames =
        input.value
        ? input.value.split(",").map(v => v.trim())
        : [];

    let currentIds =
        hiddenInput.value
        ? hiddenInput.value.split(",").map(v => v.trim())
        : [];

    // AVOID DUPLICATE
    if(!currentIds.includes(selectedId)){

        currentNames.push(selectedName);

        currentIds.push(selectedId);
    }

    // SET VALUES
    input.value =
        currentNames.join(", ");

    hiddenInput.value =
        currentIds.join(",");

    resultBox.style.display = "none";

    // CATEGORY => LOAD TYPE
    if(hiddenId === "category"){

        const typeField =
            document.getElementById("type");

        const typeInput =
            document.getElementById("typeInput");

        if(typeField){
            typeField.value = "";
        }

        if(typeInput){
            typeInput.value = "";
        }

        loadTypes(selectedId);
    }

    return;
}

        // ================= ADD NEW =================
        const addBtn =
            e.target.closest(".search-add-more");

        if(addBtn){

            const type =
                addBtn.dataset.type;

            const value =
                input.value.trim();

            if(!value){

                showToast(
                    `Please enter ${type} name`,
                    "warning"
                );

                return;
            }

            let bodyData = {
                name: value
            };

            // TYPE NEED CATEGORY
            if(type === "type"){

                const categoryId =
                    document.getElementById("category")?.value;

                if(!categoryId){

                    showToast(
                        "Please select category first",
                        "warning"
                    );

                    return;
                }

                bodyData.category_id =
                    categoryId;
            }

            fetch(`/api/add-${type}/`, {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "X-CSRFToken":
                        getCSRFToken()
                },

                body:
                    JSON.stringify(bodyData)

            })

            .then(res => res.json())

            .then(data => {

                if(data.error){

                    showToast(
                        data.error,
                        "error"
                    );

                    return;
                }

                const div =
                    document.createElement("div");

                div.className =
                    "search-item";

                div.setAttribute(
                    "data-id",
                    data.id
                );

                div.setAttribute(
                    "data-name",
                    data.name.toLowerCase()
                );

                div.innerText =
                    data.name;

                resultBox.insertBefore(
                    div,
                    addBtn
                );

                input.value =
                    data.name;

                hiddenInput.value =
                    data.id;

                resultBox.style.display =
                    "none";

                showToast(
                    `${type} added successfully`,
                    "success"
                );

            })

            .catch(() => {

                showToast(
                    `Failed to add ${type}`,
                    "error"
                );

            });

        }

    });

    // ================= OUTSIDE CLICK =================
    document.addEventListener("click", function(e){

        if(
            !resultBox.contains(e.target)
            &&
            e.target !== input
        ){

            resultBox.style.display = "none";
        }

    });

}

// ================= LOAD CATEGORY =================
function loadCategories(){

    fetch('/api/categories/')

    .then(res => res.json())

    .then(data => {

        const resultBox =
            document.getElementById(
                "categoryResult"
            );

        if(!resultBox){
            return;
        }

        resultBox.innerHTML = "";

        data.forEach(item => {

            resultBox.innerHTML += `

                <div class="search-item"
                     data-id="${item.id}"
                     data-name="${item.name.toLowerCase()}">

                    ${item.name}

                </div>

            `;
        });

        resultBox.innerHTML += `

            <div class="search-add-more"
                 data-type="category">

                + Add New Category

            </div>

        `;

    })

    .catch(() => {

        showToast(
            "Failed to load categories",
            "error"
        );

    });

}

// ================= LOAD TYPES =================
function loadTypes(categoryId){

    if(!categoryId){
        return;
    }

    fetch(`/api/types/${categoryId}/`)

    .then(res => res.json())

    .then(data => {

        const typeResult =
            document.getElementById(
                "typeResult"
            );

        if(!typeResult){
            return;
        }

        typeResult.innerHTML = "";

        data.forEach(item => {

            typeResult.innerHTML += `

                <div class="search-item"
                     data-id="${item.id}"
                     data-name="${item.name.toLowerCase()}">

                    ${item.name}

                </div>

            `;
        });

        typeResult.innerHTML += `

            <div class="search-add-more"
                 data-type="type">

                + Add New Type

            </div>

        `;

    })

    .catch(() => {

        showToast(
            "Failed to load types",
            "error"
        );

    });

}

// ================= DISCOUNT =================
function calculateDiscount() {

    let mrp =
        parseFloat(
            document.getElementById('mrp')?.value
        ) || 0;

    let discount =
        parseFloat(
            document.getElementById('discount')?.value
        ) || 0;

    if (discount > mrp) {

        showToast(
            "Discount cannot be greater than MRP",
            "error"
        );

        const discountField =
            document.getElementById('discount');

        if(discountField){
            discountField.value = "";
        }

        return;
    }

    let finalPrice =
        mrp - discount;

    let percent =
        mrp
        ? ((discount / mrp) * 100).toFixed(2)
        : 0;

    const finalPriceField =
        document.getElementById('final_price');

    const percentField =
        document.getElementById('discount_percent');

    if(finalPriceField){

        finalPriceField.value =
            finalPrice;
    }

    if(percentField){

        percentField.value =
            percent + "%";
    }
}

// ================= RENDER IMAGES =================
function renderImages(){

    let container =
        document.getElementById(
            "previewContainer"
        );

    if(!container){
        return;
    }

    container.innerHTML = "";

    selectedImages.forEach((file, index) => {

        let div =
            document.createElement("div");

        div.className = "img-box";

        div.draggable = true;

        let img =
            document.createElement("img");

        if(file.isOld){

            img.src = file.preview;

        }else{

            img.src =
                URL.createObjectURL(file.file);
        }

        if(index === 0){

            let badge =
                document.createElement("div");

            badge.className =
                "main-badge";

            badge.innerText =
                "Main Image";

            div.appendChild(badge);
        }

        let actions =
            document.createElement("div");

        actions.className =
            "img-actions";

        let del =
            document.createElement("button");

        del.innerHTML =
            `<i class="bi bi-trash"></i>`;

        del.className =
            "delete-btn";

        del.onclick = () => {

            selectedImages.splice(index, 1);

            renderImages();

            showToast(
                "Image removed",
                "error"
            );
        };

        let edit =
            document.createElement("button");

        edit.innerHTML =
            `<i class="bi bi-pencil"></i>`;

        edit.className =
            "edit-btn";

        edit.onclick =
            () => editImage(index);

        actions.appendChild(edit);

        actions.appendChild(del);

        div.appendChild(img);
if(file.color || file.size){

    let info =
        document.createElement("div");

    info.style.position = "absolute";
    info.style.bottom = "5px";
    info.style.left = "5px";
    info.style.background = "rgba(0,0,0,0.7)";
    info.style.color = "#fff";
    info.style.padding = "3px 8px";
    info.style.fontSize = "11px";
    info.style.borderRadius = "4px";

    info.innerHTML =
        `Color: ${file.color}<br>Size: ${file.size}`;

    div.appendChild(info);
}
        div.appendChild(actions);

        div.addEventListener(
            "dragstart",
            (e) => {

            e.dataTransfer.setData(
                "index",
                index
            );

        });

        div.addEventListener(
            "dragover",
            (e) => e.preventDefault()
        );

        div.addEventListener(
            "drop",
            (e) => {

            e.preventDefault();

            let from =
                e.dataTransfer.getData("index");

            let to = index;

            let item =
                selectedImages.splice(from, 1)[0];

            selectedImages.splice(
                to,
                0,
                item
            );

            renderImages();

            showToast(
                "Image reordered"
            );

        });

        container.appendChild(div);

    });

}

// ================= EDIT IMAGE =================
function editImage(index){

    let input =
        document.createElement("input");

    input.type = "file";

    input.accept = "image/*";

    input.onchange = function(e){

        let file =
            e.target.files[0];

        if(file){

            selectedImages[index] =
                file;

            renderImages();

            showToast(
                "Image updated"
            );
        }

    };

    input.click();

}

// ================= LOAD EDIT PRODUCT =================
function loadEditProduct(id){

    fetch(`/api/add-product/?id=${id}`)

    .then(res => res.json())

    .then(data => {

        console.log(data);

        // ================= BASIC =================
        document.getElementById("name").value =
            data.name || "";

        document.getElementById("mrp").value =
            data.mrp || "";

        document.getElementById("discount").value =
            data.discount || "";

        document.getElementById("stock").value =
            data.stock || "";

        document.getElementById("description").value =
            data.description || "";
        document.getElementById("is_featured").checked =
            data.is_featured || false;
        // ================= CATEGORY =================
        document.getElementById("category").value =
            data.category || "";

        document.getElementById("categoryInput").value =
            data.category_name || "";

        // ================= COLOR =================
document.getElementById("color").value =
    data.colors
    ? data.colors.join(",")
    : "";

document.getElementById("colorInput").value =
    data.color_names
    ? data.color_names.join(", ")
    : "";

        // ================= SIZE =================
document.getElementById("size").value =
    data.sizes
    ? data.sizes.join(",")
    : "";

document.getElementById("sizeInput").value =
    data.size_names
    ? data.size_names.join(", ")
    : "";

        // ================= TYPE =================
        loadTypes(data.category);

        setTimeout(() => {

            document.getElementById("type").value =
                data.type || "";

            document.getElementById("typeInput").value =
                data.type_name || "";

        }, 500);

        // ================= CALCULATE =================
        calculateDiscount();

        // ================= IMAGES =================
        selectedImages = [];

        if(data.images){

            data.images.forEach(img => {

                selectedImages.push({
    preview: img.image,
    color: img.color || "",
    size: img.size || "",
    isOld: true
});

            });

        }

        renderImages();

    })

    .catch((error) => {

        console.log(error);

        showToast(
            "Failed to load product",
            "error"
        );

    });

}

// ================= PAGE LOAD =================
document.addEventListener(
    "DOMContentLoaded",
    function () {

    // ================= SEARCH INIT =================
    setupSearch(
        "categoryInput",
        "categoryResult",
        "category"
    );

    setupSearch(
        "typeInput",
        "typeResult",
        "type"
    );

    setupSearch(
        "colorInput",
        "colorResult",
        "color"
    );

    setupSearch(
        "sizeInput",
        "sizeResult",
        "size"
    );

    loadCategories();

    // ================= EDIT MODE =================
    const params =
        new URLSearchParams(
            window.location.search
        );

    editProductId =
        params.get("edit");

    if(editProductId){

        isEditMode = true;

        const heading =
            document.querySelector("h3");

        if(heading){

            heading.innerText =
                "Edit Product";
        }

        const submitBtnText =
            document.getElementById(
                "submitBtn"
            );

        if(submitBtnText){

            submitBtnText.innerText =
                "Update Product";
        }

        loadEditProduct(editProductId);
    }

    const fileInput =
        document.getElementById("imageInput");

    const uploadBox =
        document.querySelector(
            ".image-upload-box"
        );

    // ================= DISCOUNT =================
    document.getElementById('mrp')
    ?.addEventListener(
        'input',
        calculateDiscount
    );

    document.getElementById('discount')
    ?.addEventListener(
        'input',
        calculateDiscount
    );

// ================= HANDLE FILES (UNLIMITED) =================
    function handleFiles(files) {
        const color = document.getElementById("imageColor").value;
        const size = document.getElementById("imageSize").value;

        if(!color || !size){
            showToast("Please select image color and size first", "warning");
            return;
        }

        for(let i = 0; i < files.length; i++){
            if(!files[i].type.startsWith("image/")){
                showToast("Only images allowed", "error");
                continue;
            }
            selectedImages.push({
                file: files[i],
                color: color,
                size: size
            });
        }

        renderImages();
        showToast("Images added successfully");
    }

    // ================= FILE CLICK =================
    if(uploadBox && fileInput){

        uploadBox.addEventListener(
            "click",
            () => fileInput.click()
        );
    }

    // ================= FILE CHANGE =================
    if(fileInput){

        fileInput.addEventListener(
            "change",
            function (e) {

            handleFiles(e.target.files);

            this.value = "";

        });

    }

    // ================= DRAG DROP =================
    if(uploadBox){

        uploadBox.addEventListener(
            "dragover",
            (e) => {

            e.preventDefault();

            uploadBox.classList.add(
                "dragover"
            );

        });

        uploadBox.addEventListener(
            "dragleave",
            () => {

            uploadBox.classList.remove(
                "dragover"
            );

        });

        uploadBox.addEventListener(
            "drop",
            (e) => {

            e.preventDefault();

            uploadBox.classList.remove(
                "dragover"
            );

            handleFiles(
                e.dataTransfer.files
            );

        });

    }

    // ================= INPUT ERROR REMOVE =================
    const formControls =
        document.querySelectorAll(
            ".form-control"
        );

    formControls.forEach(input => {

        input.addEventListener(
            "input",
            () => {

            input.classList.remove(
                "input-error"
            );

            let error =
                document.getElementById(
                    `error-${input.id}`
                );

            if(error){

                error.innerText = "";
            }

        });

    });

    // ================= SUBMIT =================
    const submitBtn =
        document.getElementById(
            "submitBtn"
        );

    if(submitBtn){

        submitBtn.addEventListener(
            "click",
            function(e){

            e.preventDefault();

            clearErrors();

            let name =
                document.getElementById('name')
                ?.value.trim();

            let category =
                document.getElementById('category')
                ?.value;

            let type =
                document.getElementById('type')
                ?.value;

            let color =
                document.getElementById('color')
                ?.value;

            let size =
                document.getElementById('size')
                ?.value;

            let stock =
                document.getElementById('stock')
                ?.value;

            let description =
                document.getElementById('description')
                ?.value;

            let mrp =
                document.getElementById('mrp')
                ?.value;

            let discount =
                document.getElementById('discount')
                ?.value;

            let isValid = true;

            if (!name) {

                showError(
                    "name",
                    "Product name is required"
                );

                isValid = false;
            }

            if (!category) {

                showError(
                    "category",
                    "Please select category"
                );

                isValid = false;
            }

            if (!type) {

                showError(
                    "type",
                    "Please select type"
                );

                isValid = false;
            }

            if (!color) {

                showError(
                    "color",
                    "Please select color"
                );

                isValid = false;
            }

            if (!size) {

                showError(
                    "size",
                    "Please select size"
                );

                isValid = false;
            }

            if (!mrp) {

                showError(
                    "mrp",
                    "MRP is required"
                );

                isValid = false;
            }

            if (discount === "") {

                showError(
                    "discount",
                    "Discount is required"
                );

                isValid = false;
            }

            if (!stock) {

                showError(
                    "stock",
                    "Stock is required"
                );

                isValid = false;
            }

            if (!description) {

                showError(
                    "description",
                    "Description is required"
                );

                isValid = false;
            }

            // ================= IMAGE VALIDATION =================
            if (
                !isEditMode &&
                selectedImages.length === 0
            ) {

                showToast(
                    "Please upload at least 1 image",
                    "warning"
                );

                isValid = false;
            }

            if (!isValid) {

                showToast(
                    "Please fix errors before submitting",
                    "warning"
                );

                return;
            }

            let formData =
                new FormData();

            formData.append('name', name);
            formData.append('category', category);
            formData.append('type', type);
// COLORS
color.split(",").forEach(id => {

    formData.append(
        "colors",
        id.trim()
    );

});

// SIZES
size.split(",").forEach(id => {

    formData.append(
        "sizes",
        id.trim()
    );

});
            formData.append('stock', stock);
            formData.append('description', description);
            formData.append('mrp', mrp);
            formData.append('discount', discount);
            let isFeatured =
                document.getElementById("is_featured")
                ?.checked;

            formData.append(
                "is_featured",
                isFeatured
            );

            // ================= EDIT ID =================
            if(isEditMode){
                formData.append("id", editProductId);
            }

            selectedImages.forEach(item => {
                if(!item.isOld){
                    formData.append("images", item.file);
                    
                    formData.append("image_colors", item.color || "");
                    formData.append("image_sizes", item.size || "");
                }
            });

            showToast(

                isEditMode
                ? "Updating product..."
                : "Uploading product...",

                "warning"
            );

            fetch('/api/add-product/', {

                method:
                    isEditMode
                    ? 'PATCH'
                    : 'POST',

                headers: {

                    'X-CSRFToken':
                        getCSRFToken()

                },

                body: formData

            })

            .then(res => res.json())

            .then(data => {

                if(data.success === false){

                    showToast(
                        data.message ||
                        "Something went wrong",
                        "error"
                    );

                    return;
                }

                showToast(

                    isEditMode
                    ? "Product updated successfully 🎉"
                    : "Product added successfully 🎉",

                    "success"
                );

                if(isEditMode){

                    setTimeout(() => {

                        window.location.href =
                            "/dashboard/product-list/";

                    }, 1200);

                    return;
                }

                const form =
                    document.getElementById(
                        "productForm"
                    );

                if(form){
                    form.reset();
                }

                selectedImages = [];

                renderImages();

            })

            .catch((error) => {

                console.log(error);

                showToast(
                    "Something went wrong!",
                    "error"
                );

            });

        });

    }

});