var nactions=4;

$("li.action a").click(function(event){
    event.preventDefault();
    console.log("p");
    var myli=$(this).parents("li.action");
    myli.siblings("li.action").hide();
});

$(".nomipropri").click(function(event){
    event.preventDefault();
    var myli=$(this).parents("li.action");
    console.log("nome");
    s='<table>'
    s+='<tr><td>paradigma:</td><td> <SELECT NAME="paradigma">';
    {% for par in paradigma_propri %}
    s+='<OPTION VALUE="{{ par.id }}">{{ par }}</OPTION>';
    {% endfor %}
    s+='</SELECT></td></tr>';
    s+='<tr><td>tema (se diverso):</td><td><input type="text" name="tema"/></td></tr>';
    s+='</table>';
    myli.append(s);
    $(this).replaceWith('<a href="" class="savenomipropri">&#x21c9; salva come nome proprio</a>');
});

$(".savenomipropri").click(function(event){
    event.preventDefault();
});