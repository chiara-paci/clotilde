/*** get selection ***/

var get_selection = function(el) {
    var start = 0, end = 0, normalizedValue, range,
    textInputRange, len, endRange;
    
    /** not IE **/
    if ( (typeof el.selectionStart == "number") 
	&& (typeof el.selectionEnd == "number") )
	return { start: el.selectionStart, end: el.selectionEnd };
    
    /** IE **/
    
    range = document.selection.createRange();
    L = el.value.length;
    
    if ( (!range) || (range.parentElement() != el) )
	return { start: L, end: L };
    
    normalizedValue = el.value.replace(/\r\n/g, "\n");
    
    // Create a working TextRange that lives only in the input
    textInputRange = el.createTextRange();
    textInputRange.moveToBookmark(range.getBookmark());
    
    // Check if the start and end of the selection are at the very end
    // of the input, since moveStart/moveEnd doesn't return what we want
    // in those cases
    endRange = el.createTextRange();
    endRange.collapse(false);
    
    if (textInputRange.compareEndPoints("StartToEnd", endRange) > -1)
	return { start: L, end: L };

    start = -textInputRange.moveStart("character", -L);
    start += normalizedValue.slice(0, start).split("\n").length - 1;
	
    if (textInputRange.compareEndPoints("EndToEnd", endRange) > -1)
	return { start: start, end: L };

    end = -textInputRange.moveEnd("character", -L);
    end += normalizedValue.slice(0, end).split("\n").length - 1;

    return { start: start, end: end };

};

/*** manipulate selection ***/

var exec_function_on_selection = function(text_area,callable) {
    var L = text_area.val().length;
    var sel=get_selection(text_area[0]);
    var old_text = text_area.val();
    var new_text = old_text.substring(0,sel.start) + callable(old_text.substring(sel.start,sel.end)) + old_text.substring(sel.end,L);
    text_area.val(new_text);
};

var insert_text = function(text_area,tag) {
    var L = text_area.val().length;
    var sel=get_selection(text_area[0]);
    var old_text = text_area.val();
    var new_text = old_text.substring(0,sel.start) + tag + old_text.substring(sel.start,L);
    text_area.val(new_text);
};

var insert_tag = function(text_area,open_tag,close_tag) {
    var L = text_area.val().length;
    var sel=get_selection(text_area[0]);
    var old_text = text_area.val();
    var new_text = old_text.substring(0,sel.start) + open_tag + old_text.substring(sel.start,sel.end) + close_tag + old_text.substring(sel.end,L);
    text_area.val(new_text);
};

/*** string functions ***/

var actions = new Array();

actions["action_upper"] = function(text){  
    return text.toUpperCase();
};

actions["action_lower"] = function(text){  
    return text.toLowerCase();
};

/*** set buttons ***/

var set_simple_tag_button = function(text_area,button,tag) {
    button.click(function(event) {
	event.preventDefault();
	insert_tag(text_area,"["+tag+"]","[/"+tag+"]");
    });
};

var set_single_tag_button = function(text_area,button,tag) {
    button.click(function(event) {
	event.preventDefault();
	insert_text(text_area,"["+tag+"/]");
    });
};

var set_outer_tag_button = function(text_area,button,tag,args,txt) {
    button.click(function(event) {
	insert_text(text_area,"["+tag+" "+args+"]"+txt+"[/"+tag+"]");
    });
};

var set_function_tag_button = function(text_area,button,callable_id) {
    button.click(function(event) {
	event.preventDefault();
	exec_function_on_selection(text_area,actions[callable_id]);
    });
};

/*** main ***/

$(document).ready(
    function() {
	$("div.editor").each(
	    function(index) {
		var text_area=$(this).children("textarea").first();	
		var toolbars=$(this).children("div.toolbar");
		toolbars.each(
		    function(tindex){
			var buttons=$(this).children("a");
			buttons.each(
			    function(bindex){
				switch ( $(this).attr("name") ) {
				case "vspace":
				case "hspace":
				    set_single_tag_button(text_area,$(this),$(this).attr("name"));
				    break;
				case "action_upper":
				case "action_lower":
				    set_function_tag_button(text_area,$(this),$(this).attr("name"));
				    break;
				default:
				    set_simple_tag_button(text_area,$(this),$(this).attr("name"));
				}
			    });
		    });
	    });

	$("a.santa-clara-button").each(
	    function(index){
		var name=$(this).attr("name");
		var txt=$(this).children("span.hidden").first().text();
		var params=name.split(":");
		var text_area=$( '#id_'+params.shift() );
		var tag=params.shift();
		var args=params.join(" ");
		set_outer_tag_button(text_area,$(this),tag,args,txt)
	    });
	
    });

