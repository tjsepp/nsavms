$(document).ready(function() {
    $("#hint_id_interest").remove();
    $('#id_interest').multiselect({
        includeSelectAllOption: true,
        enableCaseInsensitiveFiltering: true,
        nonSelectedText: 'Add Interests',
        buttonWidth: '400px',
        maxHeight: 200
    });

});


$(document).ready(function() {
    $('.datatable').DataTable({
            "pagingType": "full_numbers",
            "bLengthChange": false,
            "iDisplayLength": 1000,
                "scrollY":'65vh',
                "scrollCollapse": true,
                "bStateSave": true,
                "searchDelay": 350,
                "dom": 'frtipB',

                buttons: [
                    {
                        extend: 'collection',
                        text: 'Export',
                        buttons: [
                            'copy',
                            'excel',
                            'csv',
                            {
                                extend: 'pdfHtml5',
                                orientation: 'landscape'

                             },
                            'print'
                        ]
                    }
                ]
    }
    );

} );



$(document).ready(function() {
    $('.datatableNoReport').DataTable({
            "paging": false,
            "bLengthChange": false,
            "iDisplayLength": 1000,
                "scrollY":'65vh',
                "scrollCollapse": true,
                "bStateSave": true,
                "searchDelay": 350,
                "aaSorting": []
    }
    );

} );

$(document).ready(function() {
    $('.recruitingTable').DataTable({
            "bLengthChange": false,
            "iDisplayLength": 1000,
                "scrollY":        '50vh',
                "scrollCollapse": true,
                "bStateSave": true,
                "dom": 'frtipB',

                buttons: [
                    {
                        extend: 'collection',
                        text: 'Export',
                        buttons: [
                            'copy',
                            'excel',
                            'csv',
                            {
                                extend: 'pdfHtml5',
                                orientation: 'landscape'

                             }

                        ]
                    }
                ]
        }
    );
} );


$(document).ready(function () {
    $('#ProfileNagModal').modal('show');
});

$(document).ready(function () {
    $('.select2It').select2({
         placeholder: "Select an event"
    });
});

$(document).ready(function () {
    $('.select2It2').select2({
         placeholder: "Select an event"
    });
});


$(document).ready(function () {
    $('.selectVol').select2({
         placeholder: "Select a volunteer"
    });
});


$(document).ready(function () {
    $('.volunteerSelect').select2({
         placeholder: "Select a volunteer"
    });
});

$(document).ready(function () {
    $('#id_linkedUser__interest').select2({
         placeholder: "Select Interests"
    });
});

$(document).ready(function () {
    $('#id_family__students__grade').select2({
         placeholder: "Select Grades"
    });
});

$(document).ready(function () {
    $('#id_family__students__teacher').select2({
         placeholder: "Select Teachers"
    });
});

