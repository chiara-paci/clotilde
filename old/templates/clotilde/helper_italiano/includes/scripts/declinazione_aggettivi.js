var refresh_example = function() {
    {% for deg,rules in arules %}
    $("#{{ deg }}singolaremaschile").replaceWith('<table id="{{ deg }}singolaremaschile"></table>');
    $("#{{ deg }}singolarefemminile").replaceWith('<table id="{{ deg }}singolarefemminile"></table>');
    $("#{{ deg }}pluralemaschile").replaceWith('<table id="{{ deg }}pluralemaschile"></table>');
    $("#{{ deg }}pluralefemminile").replaceWith('<table id="{{ deg }}pluralefemminile"></table>');
    var sm{{ deg }}=$("#{{ deg }}singolaremaschile");
    var sf{{ deg }}=$("#{{ deg }}singolarefemminile");
    var pm{{ deg }}=$("#{{ deg }}pluralemaschile");
    var pf{{ deg }}=$("#{{ deg }}pluralefemminile");
    {% endfor %}

    var S=$("#stem").val();

    console.log(S);
    if (S=="") return;

    url="/tools/helper_italiano/declinazione_aggettivi/{{ par.id }}/"+S+".json";
    var args = { 
	type:"GET", url:url, data:{}, 
	dataType: "json",
	complete: function(json){ 
	    var newT= $.parseJSON(json.responseText);

	    {% for deg,rules in arules %}
	    for(i=0;i<newT.{{ deg }}singolaremaschile.length;i++){
		t=newT.{{ deg }}singolaremaschile[i][0];
		flag=newT.{{ deg }}singolaremaschile[i][1];
		if (flag) sm{{ deg }}.append('<tr><td><b>'+t+'</b></td></tr>');
		else sm{{ deg }}.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.{{ deg }}singolarefemminile.length;i++){
		t=newT.{{ deg }}singolarefemminile[i][0];
		flag=newT.{{ deg }}singolarefemminile[i][1];
		if (flag) sf{{ deg }}.append('<tr><td><b>'+t+'</b></td></tr>');
		else sf{{ deg }}.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.{{ deg }}pluralemaschile.length;i++){
		t=newT.{{ deg }}pluralemaschile[i][0];
		flag=newT.{{ deg }}pluralemaschile[i][1];
		if (flag) pm{{ deg }}.append('<tr><td><b>'+t+'</b></td></tr>');
		else pm{{ deg }}.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.{{ deg }}pluralefemminile.length;i++){
		t=newT.{{ deg }}pluralefemminile[i][0];
		flag=newT.{{ deg }}pluralefemminile[i][1];
		if (flag) pf{{ deg }}.append('<tr><td><b>'+t+'</b></td></tr>');
		else pf{{ deg }}.append('<tr><td>'+t+'</td></tr>');
	    }
	    {% endfor %}

	}
    };
    $.ajax(args);
};

$("#refresh").click(function(event){
    event.preventDefault();
    refresh_example();
});

$("#save").hide();
$("#edit").show();

$("#save").click(function(event){
    event.preventDefault();
    $("#save").hide();
    $("#edit").show();
});

$("#edit").click(function(event){
    event.preventDefault();
    $("#edit").hide();
    $("#save").show();
});

