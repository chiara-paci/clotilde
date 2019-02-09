var refresh_example = function() {
    $("#singolaremaschile").replaceWith('<table id="singolaremaschile"></table>');
    $("#singolarefemminile").replaceWith('<table id="singolarefemminile"></table>');
    $("#pluralemaschile").replaceWith('<table id="pluralemaschile"></table>');
    $("#pluralefemminile").replaceWith('<table id="pluralefemminile"></table>');
    var sm=$("#singolaremaschile");
    var sf=$("#singolarefemminile");
    var pm=$("#pluralemaschile");
    var pf=$("#pluralefemminile");
    var S=$("#stem").val();

    console.log(S);
    if (S=="") return;

    url="/tools/helper_italiano/declinazione_nomi/{{ par.id }}/"+S+".json";
    var args = { 
	type:"GET", url:url, data:{}, 
	dataType: "json",
	complete: function(json){ 
	    var newT= $.parseJSON(json.responseText);
	    for(i=0;i<newT.singolaremaschile.length;i++){
		t=newT.singolaremaschile[i][0];
		flag=newT.singolaremaschile[i][1];
		if (flag) sm.append('<tr><td><b>'+t+'</b></td></tr>');
		else sm.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.singolarefemminile.length;i++){
		t=newT.singolarefemminile[i][0];
		flag=newT.singolarefemminile[i][1];
		if (flag) sf.append('<tr><td><b>'+t+'</b></td></tr>');
		else sf.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.pluralemaschile.length;i++){
		t=newT.pluralemaschile[i][0];
		flag=newT.pluralemaschile[i][1];
		if (flag) pm.append('<tr><td><b>'+t+'</b></td></tr>');
		else pm.append('<tr><td>'+t+'</td></tr>');
	    }
	    for(i=0;i<newT.pluralefemminile.length;i++){
		t=newT.pluralefemminile[i][0];
		flag=newT.pluralefemminile[i][1];
		if (flag) pf.append('<tr><td><b>'+t+'</b></td></tr>');
		else pf.append('<tr><td>'+t+'</td></tr>');
	    }
	}
    };
    $.ajax(args);
};

$("#refresh").click(function(event){
    event.preventDefault();
    refresh_example();
});

