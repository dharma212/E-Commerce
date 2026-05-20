/* =========================================
TAB SYSTEM
========================================= */

function showTab(tabName, element){

    document
    .querySelectorAll(".tab-content-box")
    .forEach(tab => {

        tab.classList.add("d-none");

    });

    const activeTab =
        document.getElementById(
            tabName + "Tab"
        );

    if(activeTab){

        activeTab.classList.remove(
            "d-none"
        );

    }

    document
    .querySelectorAll(".sidebar-link")
    .forEach(btn => {

        btn.classList.remove("active");

    });

    if(element){

        element.classList.add("active");

    }

}

/* =========================================
TOAST
========================================= */

function showToast(
    message,
    type = "success"
){

    const oldToast =
        document.querySelector(
            ".custom-toast"
        );

    if(oldToast){

        oldToast.remove();

    }

    const toast =
        document.createElement("div");

    toast.className =
        "custom-toast";

    toast.innerText =
        message;

    toast.style.position =
        "fixed";

    toast.style.top =
        "20px";

    toast.style.right =
        "20px";

    toast.style.padding =
        "14px 20px";

    toast.style.borderRadius =
        "12px";

    toast.style.color =
        "#fff";

    toast.style.fontWeight =
        "600";

    toast.style.zIndex =
        "999999";

    toast.style.background =
        type === "error"
        ? "#dc3545"
        : "#28a745";

    document.body.appendChild(
        toast
    );

    setTimeout(() => {

        toast.remove();

    }, 3000);

}

/* =========================================
CSRF TOKEN
========================================= */

function getCSRFToken(){

    const token =
        document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

    return token
        ? token.value
        : "";

}

/* =========================================
ENABLE EDIT
========================================= */

function enableEdit(field){

    const input =
        document.getElementById(field);

    const text =
        document.getElementById(
            field + "Text"
        );

    if(!input || !text){
        return;
    }

    input.classList.remove(
        "d-none"
    );

    text.parentElement.classList.add(
        "d-none"
    );

    input.value =
        text.innerText.trim() === "--"
        ? ""
        : text.innerText.trim();

    input.focus();

}

/* =========================================
SAVE FIELD
========================================= */

async function saveField(field){

    try{

        const input =
            document.getElementById(field);

        if(!input){
            return;
        }

        const value =
            input.value
            ? input.value.trim()
            : "";

        const errorBox =
            document.getElementById(
                field + "Error"
            );

        if(errorBox){

            errorBox.innerText = "";

        }

        if(!value){

            if(errorBox){

                errorBox.innerText =
                    field + " is required";

            }

            showToast(
                field + " is required",
                "error"
            );

            return;

        }

        if(
            field === "email" &&
            !value.includes("@")
        ){

            if(errorBox){

                errorBox.innerText =
                    "Invalid email";

            }

            showToast(
                "Invalid email",
                "error"
            );

            return;

        }

        if(field === "phone"){

            const regex =
                /^[0-9]{10}$/;

            if(!regex.test(value)){

                if(errorBox){

                    errorBox.innerText =
                        "Phone must be 10 digits";

                }

                showToast(
                    "Phone must be 10 digits",
                    "error"
                );

                return;

            }

        }

        const response =
            await fetch(
                "/api/user-profile/",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":"application/json",
                        "X-CSRFToken":
                        getCSRFToken()
                    },

                    body:JSON.stringify({
                        [field]:value
                    })
                }
            );

        if(!response.ok){

            showToast(
                "Update failed",
                "error"
            );

            return;

        }

        const text =
            document.getElementById(
                field + "Text"
            );

        if(text){

            text.innerText = value;

            updateProfileProgress();

            text.parentElement.classList.remove(
                "d-none"
            );

        }

        input.classList.add(
            "d-none"
        );

        showToast(
            field + " updated successfully"
        );

    }catch(error){

        console.log(error);

        showToast(
            "Something went wrong",
            "error"
        );

    }

}

/* =========================================
PROFILE AUTO SAVE
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){

        const profileFields = [

            "username",
            "email",
            "phone",
            "city",
            "bio"

        ];

        profileFields.forEach(field => {

            const input =
                document.getElementById(
                    field
                );

            if(input){

                input.addEventListener(
                    "blur",
                    function(){

                        saveField(field);

                    }
                );

            }

        });

    }
);

/* =========================================
IMAGE UPLOAD
========================================= */

const profileImageInput =
    document.getElementById(
        "profileImageInput"
    );

if(profileImageInput){

    profileImageInput.addEventListener(
        "change",
        async function(){

            try{

                const file =
                    this.files[0];

                if(!file){
                    return;
                }

                const formData =
                    new FormData();

                formData.append(
                    "image",
                    file
                );

                const response =
                    await fetch(
                        "/api/upload-image/",
                        {
                            method:"POST",

                            headers:{
                                "X-CSRFToken":
                                getCSRFToken()
                            },

                            body:formData
                        }
                    );

                const data =
                    await response.json();

                if(response.ok){

                    const preview1 =
                        document.getElementById(
                            "profilePreview"
                        );

                    const preview2 =
                        document.getElementById(
                            "modalPreviewImage"
                        );

                    if(preview1){

                        preview1.src =
                            data.image;

                    }

                    if(preview2){

                        preview2.src =
                            data.image;

                    }

                    updateProfileProgress();

                    showToast(
                        "Profile image updated"
                    );

                }
                else{

                    showToast(
                        "Upload failed",
                        "error"
                    );

                }

            }catch(error){

                console.log(error);

                showToast(
                    "Upload error",
                    "error"
                );

            }

        }
    );

}

/* =========================================
ADDRESS FORM
========================================= */

const addressForm =
    document.getElementById(
        "addressForm"
    );

if(addressForm){

    addressForm.addEventListener(
        "submit",
        async function(e){

            e.preventDefault();

            try{

                const formData =
                    new FormData(this);

                const response =
                    await fetch(
                        "/address/add/",
                        {
                            method:"POST",

                            headers:{
                                "X-CSRFToken":
                                getCSRFToken()
                            },

                            body:formData
                        }
                    );

                const data =
                    await response.json();

                if(response.ok){

                    showToast(
                        data.message
                    );

                    setTimeout(() => {

                        location.reload();

                    }, 1000);

                }
                else{

                    showToast(
                        data.error ||
                        "Address failed",
                        "error"
                    );

                }

            }catch(error){

                console.log(error);

                showToast(
                    "Something went wrong",
                    "error"
                );

            }

        }
    );

}

/* =========================================
DELETE ADDRESS
========================================= */

async function deleteAddress(id){

    try{

        const response =
            await fetch(
                `/address/delete/${id}/`,
                {
                    method:"POST",

                    headers:{
                        "X-CSRFToken":
                        getCSRFToken()
                    }
                }
            );

        const data =
            await response.json();

        if(response.ok){

            showToast(
                data.message
            );

            setTimeout(() => {

                location.reload();

            }, 1000);

        }
        else{

            showToast(
                data.error,
                "error"
            );

        }

    }catch(error){

        console.log(error);

        showToast(
            "Delete failed",
            "error"
        );

    }

}

/* =========================================
REMOVE CART ITEM
========================================= */

document.addEventListener(
    "click",
    async function(e){

        const button =
            e.target.closest(
                ".remove-cart-btn"
            );

        if(!button){
            return;
        }

        const cartId =
            button.dataset.cartId;

        if(!cartId){

            showToast(
                "Cart ID missing",
                "error"
            );

            return;

        }

        try{

            const response =
                await fetch(
                    `/cart/remove/${cartId}/`,
                    {
                        method:"POST",

                        headers:{
                            "X-CSRFToken":
                            getCSRFToken(),

                            "X-Requested-With":
                            "XMLHttpRequest"
                        }
                    }
                );

            const data =
                await response.json();

            if(response.ok){

                showToast(
                    data.message ||
                    "Item removed"
                );

                setTimeout(() => {

                    location.reload();

                }, 800);

            }
            else{

                showToast(
                    data.error ||
                    "Remove failed",
                    "error"
                );

            }

        }catch(error){

            console.log(error);

            showToast(
                "Something went wrong",
                "error"
            );

        }

    }
);

/* =========================================
PROFILE COMPLETION
========================================= */

function updateProfileProgress(){

    const fields = [

        document.getElementById(
            "usernameText"
        ),

        document.getElementById(
            "emailText"
        ),

        document.getElementById(
            "phoneText"
        ),

        document.getElementById(
            "cityText"
        ),

        document.getElementById(
            "bioText"
        ),

        document.getElementById(
            "profilePreview"
        )

    ];

    let filled = 0;

    fields.forEach(field => {

        if(!field){
            return;
        }

        if(field.tagName === "IMG"){

            if(
                field.src &&
                !field.src.includes(
                    "default-user.png"
                )
            ){

                filled++;

            }

        }
        else{

            const value =
                field.innerText.trim();

            if(
                value !== "" &&
                value !== "--"
            ){

                filled++;

            }

        }

    });

    const percent =
        Math.round(
            (filled / fields.length) * 100
        );

    const progressBar =
        document.getElementById(
            "profileProgressBar"
        );

    const progressText =
        document.querySelector(
            ".progress-text"
        );

    if(progressBar){

        progressBar.style.width =
            percent + "%";

    }

    if(progressText){

        progressText.innerText =
            percent +
            "% Profile Completed";

    }

}

/* =========================================
OPEN IMAGE MODAL
========================================= */

function openImageModal(){

    document
    .getElementById(
        "imageModal"
    )
    .classList.add("active");

}

/* =========================================
CLOSE IMAGE MODAL
========================================= */

function closeImageModal(){

    document
    .getElementById(
        "imageModal"
    )
    .classList.remove("active");

}

/* =========================================
CLOSE MODAL OUTSIDE CLICK
========================================= */

window.addEventListener(
    "click",
    function(e){

        const modal =
            document.getElementById(
                "imageModal"
            );

        if(e.target === modal){

            closeImageModal();

        }

    }
);

/* =========================================
PAGE LOAD
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){

        updateProfileProgress();

    }
);