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
            "bLengthChange": false,
            "iDisplayLength": 100
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
         placeholder: "enter a volunteer"
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

