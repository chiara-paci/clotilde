$(".mrstatusedit").hide();
$(".mrstatusview").show();

$(".mractionedit").click(function(event){
    event.preventDefault();
    var tab=$(this).parents("table.morphrule");
    var bigtd=$(this).parents("td.mrparent");
    
    bigtd.attr("colspan",3);
    bigtd.siblings("td.example").hide();

    tab.find('span.pattern').replaceWith(function() {
	return('<input class="pattern mrule" type="text" value="'+$(this).html()+'"/>');
    });

    tab.find('span.replacement').replaceWith(function() {
	return('<input class="replacement mrule" type="text" value="'+$(this).html()+'"/>');
    });

    tab.find('span.mrempty').replaceWith(function() {
	var ret='<input class="pattern mrule" type="text" value="(.*)"/>';
	ret+="&#8614;"
	ret+='<input class="replacement mrule" type="text" value="\\1"/>';
	return(ret);
    });
    
    tab.find(".mrstatusedit").show();
    tab.find(".mrstatusview").hide();
});

$(".mractionadd").click(function(event){
    event.preventDefault();
    var tab=$(this).parents("table.morphrule");
    var row="<tr>";
    row+='<td class="regexp" id="none">';
    row+='<input class="pattern mrule" type="text" value="(.*)"/>';
    row+=" &#8614; "
    row+='<input class="replacement mrule" type="text" value="\\1"/>';
    row+=' <a href="" class="mrstatusedit mractiondelete"><img src="{{ ICON_MINI_DELETE }}"/></a>';
    row+='</td></tr>';
    tab.append(row);
    $(".mractiondelete").click(actiondelete);
});

var actiondelete=function(event){
    event.preventDefault();
    var td=$(this).parents("td.regexp");
    if (td.attr("id")=="none") {
	td.remove();
	return;
    }
    td.find("input.replacement").val('');
    td.hide();
}

$(".mractiondelete").click(actiondelete);

$(".mractionsave").click(function(event){
    event.preventDefault();
    var tab=$(this).parents("table.morphrule");
    var bigtd=$(this).parents("td.mrparent");
    var rule_oid=bigtd.attr("id");
    var regexps=[];
    var initial_num=0;
    var total_num=0;
    var data={};
    /** get data **/

    tab.find("td.regexp").each(function(){
	var pattern=$(this).find(".pattern").val();
	var replacement=$(this).find(".replacement").val();
	var rid=$(this).attr("id");
	var fprefix="form-"+total_num+"-";
	data[fprefix+"pattern"]=pattern;
	data[fprefix+"replacement"]=replacement;
	if (rid=="none") 
	    data[fprefix+"rule"]='';
	else {
	    initial_num+=1;
	    data[fprefix+"rule"]=rid;
	}
	total_num+=1;
    });

    url="/tools/helper_italiano/{{ mrtype }}/{{ paradigma.id }}/save_"+rule_oid+".json";

    data["form-TOTAL_FORMS"]=total_num;
    data["form-MAX_NUM_FORMS"]=total_num;
    data["form-INITIAL_FORMS"]=initial_num;

    console.log(data);

    var args = { 
	type:"POST", url:url, data:data, 
	dataType: "json",
	complete: function(json){ 
	    var newT= $.parseJSON(json.responseText);
	    var S;
	    var L=newT.data.length;
	    console.log(newT);
	    tab.find("tr.rule").remove();
	    if (L==0) {
		tab.append('<tr class="rule"><td class="regexp"><span class="mrempty">&nbsp;</span></td><td></td></tr>');
		return;
	    }
	    for(n=0;n<L;n++) {
		S='<tr class="rule">';
		S+='<td class="regexp" id="'+newT.data[n][0]+'">';
		S+='<span class="pattern">'+newT.data[n][1]+'</span> &#8614; ';
		S+='<span class="replacement">'+newT.data[n][2]+'</span>';
		if (newT.data[n][3])
		    S+='<img src="{{ ICON_DICT_ENTRY }}" class="mrstatusview"/>';
		S+='<a href="" id="'+newT.data[n][0]+'" class="mrstatusedit mractiondelete">';
		S+='<img src="{{ ICON_MINI_DELETE }}"/></a>';
		S+='</td></tr>';
		tab.append(S);
	    }
	    tab.find(".mractiondelete").click(actiondelete);
	    tab.find(".mrstatusedit").hide();
	    tab.find(".mrstatusview").show();
	}
    };
    $.ajax(args);

    bigtd.attr("colspan",1);
    bigtd.siblings("td.example").show();
});

