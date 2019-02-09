$(document).ready(function(){

    $(".taginput").each(function(index){
	var open_tl=$(this).find("a.taglistopen").first();
	var close_tl=$(this).find("a.taglistclose").first();
	var div_tl=$(this).find(".taglist").first();

	open_tl.show();
	close_tl.hide();
	div_tl.hide();
	
	open_tl.click(function(event){
	    close_tl.show();
	    open_tl.hide();
	    div_tl.show();
	});
	
	close_tl.click(function(event){
	    close_tl.hide();
	    open_tl.show();
	    div_tl.hide();
	});
	
	$(".taglabel").click(function(event){
	    var label=$(this).html();
	    var widget_name=$(this).data("widget-name");
	    var entry_tl=$('#id_'+widget_name);
	    entry_tl.val(label);
	});
	
    });


});
