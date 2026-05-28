$(document).ready(function(){

    var table = $('#userTable').DataTable({

        responsive:true,

        pageLength:10,

        lengthMenu:[5,10,25,50,100],

        autoWidth:false,

        ordering:true,

        searching:true,

        paging:true,

        info:true,

        language:{

            search:"Search :",

            lengthMenu:"Show _MENU_ Users",

        }

    });

    table.column(4).search(
        'Customer|Seller',
        true,
        false
    ).draw();

    $('.filter-btn').on('click', function(){

        $('.filter-btn').removeClass('active');

        $(this).addClass('active');

        var role = $(this).data('role');

        if(role === 'admin'){

            table.column(4)
                 .search('Admin')
                 .draw();

        }

        else{

            table.column(4)
                 .search(
                    'Customer|Seller',
                    true,
                    false
                 )
                 .draw();

        }

    });

});