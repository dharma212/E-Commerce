
// =======================
// LOAD CATEGORIES
// =======================
function loadCategories() {

    let cat = document.getElementById('category');

    if(!cat) return;

    fetch('/api/categories/')
    .then(res => res.json())
    .then(data => {

        cat.innerHTML = '<option value="">Select Category</option>';

        data.forEach(item => {
            cat.innerHTML += `<option value="${item.id}">${item.name}</option>`;
        });

    })
    .catch(() => {

        cat.innerHTML =
        '<option>Error loading categories</option>';

    });

}

loadCategories();


// =======================
// SHOW MESSAGE
// =======================
function showMessage(text, type="success") {
    const msg = document.getElementById('msg');
    msg.innerHTML = `
      <div class="alert alert-${type}">
        ${text}
      </div>
    `;

    setTimeout(() => {
        msg.innerHTML = "";
    }, 3000);
}


// =======================
// SUBMIT FORM
// =======================
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
const typeForm = document.getElementById('typeForm');

if(typeForm){

    typeForm.addEventListener('submit', function(e){

        e.preventDefault();

        let name = document.getElementById('type_name').value.trim();
        let category = document.getElementById('category').value;
        let btn = document.getElementById('submitBtn');

        if (!category || !name) {
            showMessage("Please fill all fields", "danger");
            return;
        }

        btn.disabled = true;
        btn.innerHTML = "Saving...";

        fetch('/api/add-type/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                name: name,
                category: category
            })
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {
                showMessage("Type added successfully", "success");
                typeForm.reset();
            } else {
                showMessage(data.message || "Something went wrong", "danger");
            }

        })
        .catch(() => {
            showMessage("Server error", "danger");
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = "Add Type";
        });

    });

}