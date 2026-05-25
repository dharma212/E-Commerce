$(document).ready(function(){
    $('#wishlistTable').DataTable({
        pageLength: 10,
        ordering: true,
        responsive: true,
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            zeroRecords: "No wishlist data found",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            paginate: {
                previous: "Prev",
                next: "Next"
            }
        }
    });
});