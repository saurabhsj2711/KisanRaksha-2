$(document).ready(function() {

var MaxInputs       = 8; //maximum input boxes allowed
var InputsWrapper   = $("#InputsWrapper"); //Input boxes wrapper ID
var AddButton       = $("#AddMoreFileBox"); //Add button ID

var x = InputsWrapper.length; //initlal text box count
var FieldCount=1; //to keep track of text box added

$(AddButton).click(function (e)  //on add input button click
{

        if(x <= MaxInputs) //max input box allowed
        {
            FieldCount++; //text box added increment
            //add input box
            $(InputsWrapper).append('<div class="row">'
                                        +'<p class="col-md-12">'
                                            +'<input type="text" placeholder="Enter disease name" class="form-control skill_list" name="disease_name[]" id="disease_name_'+ FieldCount +'"/>'
                                        +'</p>'
                                        +'<p class="col-md-12">'
                                            +'<input type="text" placeholder="Enter causes" class="form-control skill_list" name="causes[]" id="causes_'+ FieldCount +'"/>'
                                        +'</p>'
                                        +'<p class="col-md-12">'
                                            +'<textarea class="form-control rounded-0" name="symptoms[]" placeholder="Enter Symptoms" id="symptoms'+ FieldCount +'"  rows="6"></textarea>'
                                        +'</p>'
                                        +'<p class="col-md-12">'
                                            +'<textarea class="form-control rounded-0" name="management[]" placeholder="Enter Management required" id="management_'+ FieldCount +'"  rows="6"></textarea>'
                                        +'</p>'
                                        +'<p class="col-md-12">'
                                            +'<textarea class="form-control rounded-0" name="solution[]" placeholder="Enter Solution of disease" id="field5_'+ FieldCount +'"  rows="6"></textarea>'
                                        +'</p>'
                                        +'<a href="#" class="btn btn-danger removeclass">×</a>'
                                    +'</div>');
            x++; //text box increment
        }
return false;
});

$("body").on("click",".removeclass", function(e){ //user click on remove text
        if( x > 1 ) {
                $(this).parent('div').remove(); //remove text box
                x--; //decrement textbox
        }
return false;
})
 $('#submit').click(function(){
           $.ajax({
                url:"/postskill",
                method:"POST",
                data:$('#add_skills').serialize(),
                success:function(data)
                {  alert(data)
                     $('#resultbox').html(data);
                     $('#add_skills')[0].reset();
                }
           });
      });
});
