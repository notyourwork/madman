$(document).ready(function() {
    //initially the menu will be hidden menu / overleft
    $("#overleft").hide(); 
    //since menu is positioned absolutely to overlay
    //we dynamnically set height to the 
    
    //$('#overleft').height($('#nav').height()); 
    //$('#fader').height($('#nav').height()); 
    
    $('#inputArea').hide(); 

    $('#search_button').click(function(){
        $('#inputArea').slideToggle(); 
        $(this).toggleClass('nav_top_item_focus');
    });
    $("#overleft_header").click(function() {
        $("#overleft").slideToggle(); 
        $('#control_panel_button').toggleClass('nav_top_item_focus');
    });
    $("#control_panel_button").click(function() {
        $("#overleft").slideToggle(); 
        $(this).toggleClass('nav_top_item_focus');
    });

    //toggles item highlighting when clicks 
    $(".item").click(function(){
        $(this).toggleClass('item_focus'); 
    }); 
    

    //styles form elements when coming in/going out
    //of focus 
    $("input, textarea").addClass("idle");
    $("input, textarea").focus(function(){
        $(this).addClass("activeField").removeClass("idle");
    }).blur(function(){
        $(this).removeClass("activeField").addClass("idle");
    });


});
