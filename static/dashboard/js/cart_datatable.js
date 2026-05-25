$(document).ready(function() {
    $('#cartTable').DataTable({
        pageLength: 10,
        ordering: true,
        responsive: true,
        language: {
            lengthMenu: "Show _MENU_ entries",
            zeroRecords: "No matching items found",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            search: "Search:",
            paginate: {
                previous: "Prev",
                next: "Next"
            }
        }
    });
});