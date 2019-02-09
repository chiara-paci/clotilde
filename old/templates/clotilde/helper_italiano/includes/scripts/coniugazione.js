var set_example_cell = function(cid,exlist) {
    $("#"+cid).replaceWith('<table class="example" id="'+cid+'"></table>');
    if (exlist.length==0) return;
    tab=$('#'+cid);
    for(n=0;n<exlist.length;n++) 
	tab.append('<tr><td>'+exlist[n]+'</td></tr>');
};

{% for oid,wlist in example.items %}
{% if wlist %}
a={% for w,flag in wlist %}{% if forloop.first %}[{% else %},{% endif %}'{% if flag %}<b>{% endif %}{{ w }}{% if flag %}</b>{% endif %}'{% endfor %}];
{% else %}
a=[];
{% endif %}
set_example_cell("ex{{ oid }}",a);
console.log("ex{{ oid }}");
{% endfor %}

var refresh_example = function() {
    var S=$("#stem").val();
    $("table.example").replaceWith(function(){
	tid=$(this).attr("id");
	return('<table class="example" id="'+tid+'"></table>');
    });

    if (S=="") return;

    url="/tools/helper_italiano/coniugazione/{{ paradigma.id }}/"+S+".json";
    var args = { 
	type:"GET", url:url, data:{}, 
	dataType: "json",
	complete: function(json){ 
	    var newT= $.parseJSON(json.responseText);
	    var obj_id;
	    var obj_array;

	    {% for modo,rspan,tlist in finiti %}{% for tempo,persone in tlist %}
	    {% for pid,pers in persone %}
	    obj_id="ex{{ pers.oid }}";
	    obj_array=[];
	    for(n=0;n<newT.{{ pers.oid }}.length;n++) {
		if (newT.{{ pers.oid }}[n][1]) 
		    obj_array.push('<b>'+newT.{{ pers.oid }}[n][0]+'</b>');
		else
		    obj_array.push(newT.{{ pers.oid }}[n][0]);	
	    }
	    set_example_cell(obj_id,obj_array);
	    {% endfor %}{% endfor %}{% endfor %}

	    obj_id="ex{{ deverbali.infinito.oid }}";
	    obj_array=[];
	    for(n=0;n<newT.{{ deverbali.infinito.oid }}.length;n++) {
		if (newT.{{ deverbali.infinito.oid }}[n][1]) 
		    obj_array.push('<b>'+newT.{{ deverbali.infinito.oid }}[n][0]+'</b>');
		else
		    obj_array.push(newT.{{ deverbali.infinito.oid }}[n][0]);	
	    }
	    set_example_cell(obj_id,obj_array);

	    obj_id="ex{{ deverbali.gerundio.oid }}";
	    obj_array=[];
	    for(n=0;n<newT.{{ deverbali.gerundio.oid }}.length;n++) {
		if (newT.{{ deverbali.gerundio.oid }}[n][1]) 
		    obj_array.push('<b>'+newT.{{ deverbali.gerundio.oid }}[n][0]+'</b>');
		else
		    obj_array.push(newT.{{ deverbali.gerundio.oid }}[n][0]);	
	    }
	    set_example_cell(obj_id,obj_array);

            {% for tense,persone in deverbali.participio %}
	    {% for pid,pers in persone %}
	    obj_id="ex{{ pers.oid }}";
	    obj_array=[];
	    for(n=0;n<newT.{{ pers.oid }}.length;n++) {
		if (newT.{{ pers.oid }}[n][1]) 
		    obj_array.push('<b>'+newT.{{ pers.oid }}[n][0]+'</b>');
		else
		    obj_array.push(newT.{{ pers.oid }}[n][0]);	
	    }
	    set_example_cell(obj_id,obj_array);
	    {% endfor %}{% endfor %}
	}
    };
    $.ajax(args);


};

$("#refresh").click(function(event){
    event.preventDefault();
    refresh_example();
});

