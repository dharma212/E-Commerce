(function ($) {
    "use strict";
    const couponApiUrl = "/api/coupons/";
    let editingId = null;
    let dataTableInstance = null;

    // Core Toast Utility System
    window.showToast = function (message, type = 'success') {
        const container = document.getElementById("toastContainer");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `custom-toast toast-${type}`;

        let icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

        container.appendChild(toast);

        setTimeout(() => toast.classList.add("show"), 50);

        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    };

    function clearFormValidationErrors() {
        const inputs = document.querySelectorAll("#couponForm .form-control");
        const feedbacks = document.querySelectorAll("#couponForm .invalid-feedback-custom");

        inputs.forEach(input => input.classList.remove("is-invalid-custom"));
        feedbacks.forEach(fb => fb.style.display = "none");
    }

    window.openAddModal = function () {
        editingId = null;
        document.getElementById("couponForm").reset();
        clearFormValidationErrors();
        document.getElementById("modalTitle").innerText = "Add New Coupon";
        document.getElementById("saveBtn").innerText = "Save Coupon";
        $("#couponModal").modal("show");
    };

    // Live Active/Deactive Toggle Action Handler
    window.toggleCouponStatus = function (id, checkbox) {
        const isChecked = checkbox.checked;

        // Find row inside current context to update status locally if needed
        fetch(`/api/coupons/${id}/`)
            .then(res => res.json())
            .then(coupon => {
                // Modify active metric safely
                coupon.active = isChecked;

                return fetch(`/api/coupons/${id}/`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: JSON.stringify(coupon)
                });
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    let msg = isChecked ? "Coupon activated successfully!" : "Coupon deactivated successfully!";
                    showToast(msg, "success");
                } else {
                    checkbox.checked = !isChecked; // Revert change if failed
                    showToast("Failed to update status.", "error");
                }
            })
            .catch(err => {
                checkbox.checked = !isChecked; // Revert change if crashed
                showToast("Network error changing status.", "error");
            });
    };

    window.loadCoupons = function () {
        fetch(couponApiUrl)
            .then(response => response.json())
            .then(data => {
                if (dataTableInstance) {
                    dataTableInstance.destroy();
                    dataTableInstance = null;
                }

                let rows = "";
                let count = 1;

                data.forEach(coupon => {
                    let expiryDate = coupon.valid_to ? new Date(coupon.valid_to).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '-';

                    // Format display text based on discount type metric
                    let typeBadge = coupon.discount_type === 'percent'
                        ? '<span class="badge badge-warning text-dark badge-type">Percentage</span>'
                        : '<span class="badge badge-info text-white badge-type">Fixed Amt</span>';

                    let discountDisplay = coupon.discount_type === 'percent'
                        ? `${parseFloat(coupon.discount)}% OFF`
                        : `₹${parseFloat(coupon.discount)} OFF`;

                    rows += `
                <tr>
                    <td class="font-weight-bold text-muted">${count++}</td>
                    <td><span class="badge-coupon">${coupon.code}</span></td>
                    <td>${typeBadge}</td>
                    <td><span class="discount-text">${discountDisplay}</span></td>
                    <td class="font-weight-bold">₹${coupon.minimum_amount}</td>
                    <td style="color: #64748b;">${expiryDate}</td>
                    <td>
                        <label class="switch-custom">
                            <input type="checkbox" ${coupon.active ? 'checked' : ''} onclick="toggleCouponStatus(${coupon.id}, this)">
                            <span class="slider-custom"></span>
                        </label>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-action btn-edit-custom" onclick="editCoupon(${coupon.id})">
                            <i class="fa-solid fa-pencil"></i>
                        </button>
                        <button class="btn btn-action btn-delete-custom" onclick="deleteCoupon(${coupon.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
                });

                const tableBody =
                    document.getElementById("couponTableBody");

                if (tableBody) {
                    tableBody.innerHTML = rows;
                }

                if ($.fn.DataTable) {
                    dataTableInstance = $('#couponDataTable').DataTable({
                        "order": [[0, "asc"]],
                        "pageLength": 10,
                        "retrieve": true,
                        "dom": '<"d-flex justify-content-between align-items-center mb-3"lf>rt<"d-flex justify-content-between align-items-center mt-3"ip>',
                        "language": {
                            "search": "",
                            "searchPlaceholder": "Search coupons...",
                            "lengthMenu": "Show _MENU_ entries",
                            "paginate": {
                                "previous": "<i class='fa-solid fa-chevron-left'></i>",
                                "next": "<i class='fa-solid fa-chevron-right'></i>"
                            }
                        }
                    });
                }
            })
            .catch(error => console.error("Error loading coupons:", error));
    };

    window.editCoupon = function (id) {
        editingId = id;
        clearFormValidationErrors();
        document.getElementById("modalTitle").innerText = "Edit Coupon Settings";
        document.getElementById("saveBtn").innerText = "Update Coupon";

        fetch(couponApiUrl)
            .then(res => res.json())
            .then(data => {
                const coupon = data.find(c => c.id == id);
                if (coupon) {
                    document.getElementById("code").value = coupon.code;
                    document.getElementById("discount_type").value = coupon.discount_type;
                    document.getElementById("coupondiscount").value = coupon.discount;
                    document.getElementById("minimum_amount").value = coupon.minimum_amount;

                    if (coupon.valid_from) document.getElementById("valid_from").value = coupon.valid_from.slice(0, 16);
                    if (coupon.valid_to) document.getElementById("valid_to").value = coupon.valid_to.slice(0, 16);

                    $("#couponModal").modal("show");
                }
            });
    };

    window.deleteCoupon = function (id) {
        fetch(`/api/coupons/${id}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
            .then(response => response.json())
            .then(data => {
                showToast("Coupon deleted successfully!", "success");
                loadCoupons();
            })
            .catch(err => showToast("Failed to delete coupon.", "error"));
    };

    $(document).ready(function () {
        loadCoupons();

        let form = document.getElementById("couponForm");
        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                clearFormValidationErrors();

                let isValid = true;
                const fieldsToValidate = ["code", "discount_type", "coupondiscount", "minimum_amount", "valid_from", "valid_to"];

                fieldsToValidate.forEach(fieldId => {
                    const inputElement = document.getElementById(fieldId);
                    if (!inputElement || !inputElement.value.trim()) {
                        isValid = false;
                        inputElement.classList.add("is-invalid-custom");
                        const errorFeedback = inputElement.parentNode.querySelector(".invalid-feedback-custom");
                        if (errorFeedback) errorFeedback.style.display = "block";
                    }
                });

                if (!isValid) {
                    showToast("Please fill out all required fields.", "error");
                    return;
                }

                let url = editingId ? `/api/coupons/${editingId}/` : couponApiUrl;
                let method = editingId ? "PUT" : "POST";

                fetch(url, {
                    method: method,
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: JSON.stringify({
                        code: document.getElementById("code").value,
                        discount_type: document.getElementById("discount_type").value,
                        discount: document.getElementById("coupondiscount").value,
                        minimum_amount: document.getElementById("minimum_amount").value,
                        valid_from: document.getElementById("valid_from").value,
                        valid_to: document.getElementById("valid_to").value,
                        active: true
                    })
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success || data.message || data.id) {
                            $("#couponModal").modal("hide");
                            let successMsg = editingId ? "Coupon updated successfully!" : "Coupon added successfully!";
                            showToast(successMsg, "success");
                            loadCoupons();
                        } else {
                            showToast("Validation or network processing failure.", "error");
                        }
                    })
                    .catch(err => showToast("Something went wrong while processing data.", "error"));
            });
        }
    });

})(jQuery);