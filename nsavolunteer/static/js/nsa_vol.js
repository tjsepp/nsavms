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
    $('.select2It_volunteer').select2({
         placeholder: "Select a volunteer"
    });
});