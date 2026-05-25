
$(document).ready(function(){

    $('#userTable').DataTable({

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

});
