
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// ✅ FORM SUBMIT
const categoryForm = document.getElementById('categoryForm');

if(categoryForm){

    categoryForm.addEventListener('submit', function(e){

        e.preventDefault();

        let name = document.getElementById('category_name').value;
        let image = document.getElementById('category_image').files[0];

        let formData = new FormData();

        formData.append('name', name);

        if(image){
            formData.append('image', image);
        }

        fetch('/api/add-category/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            console.log(data);
        });

    });

}