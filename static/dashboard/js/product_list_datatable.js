$(document).ready(function () {

    $('#productTable').DataTable({

        destroy: true,

        pageLength: 10,

        ordering: true,

        responsive: false,

        autoWidth: false,

        scrollX: false,

        columnDefs: [

            {
                targets: -1,
                orderable: false,
                searchable: false
            }

        ],

        language: {

            lengthMenu:
                "Show _MENU_ entries",

            zeroRecords:
                "No matching products found",

            info:
                "Showing _START_ to _END_ of _TOTAL_ products",

            infoEmpty:
                "No products available",

            search:
                "",

            searchPlaceholder:
                "Search products...",

            paginate: {

                previous:
                    "<i class='bi bi-chevron-left'></i>",

                next:
                    "<i class='bi bi-chevron-right'></i>"
            }
        },

        drawCallback: function () {

            $('.delete-btn').off('click').on('click', function () {

                let id = $(this).data('id');

                deleteProduct(id);

            });

        }

    });

});