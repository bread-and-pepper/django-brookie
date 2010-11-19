$(document).ready(function() {
    update_total();
    
    // Capture ``insert-all`` and apply function below.
    $('#part-insert-all').click(function(event){
        event.preventDefault();
        insert_all();
    });

    // Each time the time changes, update the subtotal for the item.
    $('#brookie-item-content_type-object_id-group .vIntegerField').live('keyup', function(){
        var hourly_rate = $('#id_hourly_rate').val();
        var amount = $(this).val() * (hourly_rate / 60);
        $(this).parent().next().find('input').val(amount.toFixed(2));
        update_total();
    });

    // Update the amount when the hourly rate changes.
    $('.amount').each(function(){
        var amount = $(this).children(":first").attr("id");
        $('#' + amount).keyup(function(){
            update_total();
        });
    });
    
    // Update the item amount when the hourly rate changes.
    $('#id_hourly_rate').keyup(function(){
        $('.time').each(function(){
            var time = $(this).children(":first").attr("id");
            var time_number = time.split("-");
            var hourly_rate = $('#id_hourly_rate').val();
            var amount = $('#'+time).val() * (hourly_rate / 60);
            if($('#'+time).val() > 0){
                $('#id_brookie-item-content_type-object_id-' + time_number[4] + '-amount').val(amount.toFixed(2));
                update_total();
            }
        });
    });

    // Insert all Quote parts into the specific Quote.
    $('#all-parts').each(function(){
        $('.insert-part-link').click(function(event){
            event.preventDefault();
            var id = $(this).attr("id").split('-')[2];
            var text = $('#part-content-' + id).val();
            var spaces = '';
            if($("#id_content").val() != ""){
                spaces = '\n\n';
            }
            $("#id_content").val($("#id_content").val() + spaces + text);
        });
    });
});

// Update the subtotal.
function update_total(){
    var total = 0;
    $('.amount').each(function(){
        var amount = $(this).children(":first").attr("id");
        total_amount = parseFloat($('#'+amount).val());
        if(!isNaN(total_amount)){
            total += total_amount;
        }
    });  
    $('#totals_subtotal').val(total.toFixed(2));
};

// Insert a default Quote part into the specific Quote.
function insert_all(){
    $("body").find("[id*='part-content']").each(function(){
        var text = $(this).val();
        var spaces = '';
        if($("#id_content").val() != ""){
            spaces = '\n\n';
        }
        $("#id_content").val($("#id_content").val() + spaces + text);
    });
};
