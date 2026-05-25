// ================= GLOBAL =================
let selectedImages = [];

// ================= TOAST =================
function getToastContainer() {
    let container = document.getElementById("globalToastContainer");

    if (!container) {
        container = document.createElement("div");
        container.id = "globalToastContainer";
        container.style.position = "fixed";
        container.style.top = "20px";
        container.style.right = "20px";
        container.style.zIndex = "999999";
        document.body.appendChild(container);
    }
    return container;
}

function showToast(message, type = "success", duration = 3000) {
    const container = getToastContainer();

    const toast = document.createElement("div");
    toast.style.minWidth = "260px";
    toast.style.marginBottom = "10px";
    toast.style.padding = "14px 16px";
    toast.style.borderRadius = "10px";
    toast.style.color = "#fff";
    toast.style.fontSize = "14px";
    toast.style.display = "flex";
    toast.style.alignItems = "center";
    toast.style.gap = "10px";
    toast.style.boxShadow = "0 8px 20px rgba(0,0,0,0.2)";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.4s ease";

    let icon = `<i class="bi bi-check-circle-fill"></i>`;
    if (type === "error") icon = `<i class="bi bi-x-circle-fill"></i>`;
    if (type === "warning") icon = `<i class="bi bi-exclamation-triangle-fill"></i>`;

    if (type === "success") toast.style.background = "#4CAF50";
    else if (type === "error") toast.style.background = "#e74c3c";
    else if (type === "warning") toast.style.background = "#f39c12";
    else toast.style.background = "#333";

    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateX(0)";
    });

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ================= CSRF =================
function getCSRFToken() {
    let name = "csrftoken=";
    let cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim();
        if (c.startsWith(name)) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// ================= ERROR HANDLING =================
function clearErrors() {
    document.querySelectorAll(".error-text").forEach(el => el.innerText = "");
    document.querySelectorAll(".form-control").forEach(el => el.classList.remove("input-error"));
}

function showError(inputId, message) {
    let errorEl = document.getElementById(`error-${inputId}`);
    if (errorEl) errorEl.innerText = message;

    let inputEl = document.getElementById(inputId);
    if (inputEl) inputEl.classList.add("input-error");
}

// ================= NEW: DISCOUNT CALC =================
function calculateDiscount() {
    let mrp = parseFloat(document.getElementById('mrp')?.value) || 0;
    let discount = parseFloat(document.getElementById('discount')?.value) || 0;

    if (discount > mrp) {
        showToast("Discount cannot be greater than MRP", "error");
        document.getElementById('discount').value = "";
        return;
    }

    let finalPrice = mrp - discount;
    let percent = mrp ? ((discount / mrp) * 100).toFixed(2) : 0;

    document.getElementById('final_price').value = finalPrice;
    document.getElementById('discount_percent').value = percent + "%";
}

// ================= PAGE LOAD =================
document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("imageInput");
    const uploadBox = document.querySelector(".image-upload-box");

    // NEW: discount listeners
    document.getElementById('mrp')?.addEventListener('input', calculateDiscount);
    document.getElementById('discount')?.addEventListener('input', calculateDiscount);

    // ================= CATEGORY =================
fetch('/api/categories/')
.then(res => {

    if(!res.ok){
        throw new Error("API Error");
    }

    return res.json();

})
.then(data => {


    let cat = document.getElementById('category');

    if(!cat){
        console.log("Category select box not found");
        return;
    }

    cat.innerHTML = '<option value="">Select Category</option>';

    data.forEach(item => {

        cat.innerHTML += `
            <option value="${item.id}">
                ${item.name}
            </option>
        `;

    });

})
.catch((error) => {

    console.log(error);

    showToast("Failed to load category", "error");

});

    // ================= TYPE =================
    const categorySelect = document.getElementById('category');

    if(categorySelect){

        categorySelect.addEventListener('change', function () {

            let id = this.value;

            if (!id) return;

            fetch(`/api/types/${id}/`)
            .then(res => res.json())
            .then(data => {

                let type = document.getElementById('type');

                if(!type) return;

                type.innerHTML = '<option value="">Select Type</option>';

                data.forEach(item => {
                    type.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });

            })
            .catch(() => showToast("Failed to load types", "error"));

        });

    }

    // ================= HANDLE FILES =================
    function handleFiles(files) {

        if (selectedImages.length + files.length > 5) {
            showToast("Max 5 images allowed", "warning");
            return;
        }

        for (let i = 0; i < files.length; i++) {
            if (!files[i].type.startsWith("image/")) {
                showToast("Only images allowed", "error");
                continue;
            }
            selectedImages.push(files[i]);
        }

        renderImages();
        showToast("Images added successfully");
    }

    if(uploadBox && fileInput){

        uploadBox.addEventListener("click", () => fileInput.click());

    }

    fileInput.addEventListener("change", function (e) {
        handleFiles(e.target.files);
        this.value = "";
    });

    uploadBox.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadBox.classList.add("dragover");
    });

    uploadBox.addEventListener("dragleave", () => {
        uploadBox.classList.remove("dragover");
    });

    uploadBox.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadBox.classList.remove("dragover");
        handleFiles(e.dataTransfer.files);
    });

    document.querySelectorAll(".form-control").forEach(input => {
        input.addEventListener("input", () => {
            input.classList.remove("input-error");
            let error = document.getElementById(`error-${input.id}`);
            if (error) error.innerText = "";
        });
    });

    // ================= SUBMIT =================
    const submitBtn = document.getElementById("submitBtn");

    if(submitBtn){

        submitBtn.addEventListener("click", function(e){

        e.preventDefault();
        clearErrors();

        let name = document.getElementById('name').value.trim();
        let category = document.getElementById('category').value;
        let type = document.getElementById('type').value;
        let color = document.getElementById('color').value;
        let size = document.getElementById('size').value;
        let stock = document.getElementById('stock').value;
        let description = document.getElementById('description').value;
        let imageInput = document.getElementById('imageInput').value;

        // NEW
        let mrp = document.getElementById('mrp')?.value;
        let discount = document.getElementById('discount')?.value;

        let isValid = true;

        if (!name) {
            showError("name", "Product name is required");
            isValid = false;
        }

        if (!category) {
            showError("category", "Please select category");
            isValid = false;
        }

        if (!type) {
            showError("type", "Please select type");
            isValid = false;
        }
        if (!color) {
            showError("color", "Please select color");
            isValid = false;
        }

        if (!size) {
            showError("size", "Please select size");
            isValid = false;
        }

        // NEW VALIDATION
        if (!mrp) {
            showError("mrp", "MRP is required");
            isValid = false;
        }

        if (discount === "") {
            showError("discount", "Discount is required");
            isValid = false;
        }

        if (!stock) {
            showError("stock", "Stock is required");
            isValid = false;
        }

        if (!description) {
            showError("description", "Description is required");
            isValid = false;
        }

        if (selectedImages.length === 0) {
            showToast("Please upload at least 1 image", "warning");
            isValid = false;
        }

        if (selectedImages.length === 0) {
            showToast("Please upload at least 1 image", "warning");
            isValid = false;
        }

        if (!isValid) {
            showToast("Please fix errors before submitting", "warning");
            return;
        }

        let formData = new FormData();
        formData.append('name', name);
        formData.append('category', category);
        formData.append('type', type);
        formData.append('color', color);
        formData.append('size', size);
        formData.append('stock', stock);
        formData.append('description', description);

        // NEW
        formData.append('mrp', mrp);
        formData.append('discount', discount);

        selectedImages.forEach(file => {
            formData.append('images', file);
        });

        showToast("Uploading product...", "warning");

        fetch('/api/add-product/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            showToast("Product added successfully 🎉", "success");

            document.getElementById("productForm").reset();
            selectedImages = [];
            renderImages();
        })
        .catch(() => {
            showToast("Something went wrong!", "error");
        });
    });
    }
});


// ================= RENDER IMAGES =================
function renderImages(){
    let container = document.getElementById("previewContainer");
    container.innerHTML = "";

    selectedImages.forEach((file, index) => {
        let div = document.createElement("div");
        div.className = "img-box";
        div.draggable = true;

        let img = document.createElement("img");
        img.src = URL.createObjectURL(file);

        if(index === 0){
            let badge = document.createElement("div");
            badge.className = "main-badge";
            badge.innerText = "Main Image";
            div.appendChild(badge);
        }

        let actions = document.createElement("div");
        actions.className = "img-actions";

        let del = document.createElement("button");
        del.innerHTML = `<i class="bi bi-trash"></i>`;
        del.className = "delete-btn";
        del.onclick = () => {
            selectedImages.splice(index, 1);
            renderImages();
            showToast("Image removed", "error");
        };

        let edit = document.createElement("button");
        edit.innerHTML = `<i class="bi bi-pencil"></i>`;
        edit.className = "edit-btn";
        edit.onclick = () => editImage(index);

        actions.appendChild(edit);
        actions.appendChild(del);

        div.appendChild(img);
        div.appendChild(actions);

        div.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("index", index);
        });

        div.addEventListener("dragover", (e) => e.preventDefault());

        div.addEventListener("drop", (e) => {
            e.preventDefault();
            let from = e.dataTransfer.getData("index");
            let to = index;

            let item = selectedImages.splice(from, 1)[0];
            selectedImages.splice(to, 0, item);

            renderImages();
            showToast("Image reordered");
        });

        container.appendChild(div);
    });
}

// ================= EDIT IMAGE =================
function editImage(index){
    let input = document.createElement("input");
    input.type = "file";

    input.onchange = function(e){
        let file = e.target.files[0];
        if(file){
            selectedImages[index] = file;
            renderImages();
            showToast("Image updated");
        }
    };

    input.click();
}