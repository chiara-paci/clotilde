$("#showall").click(function(event){
    event.preventDefault();
    $("tr.token").show();
    $("tr.nottoken").show();
});

$("#showtoken").click(function(event){
    event.preventDefault();
    $("tr.token").show();
    $("tr.nottoken").hide();
});

$("#shownottoken").click(function(event){
    event.preventDefault();
    $("tr.token").hide();
    $("tr.nottoken").show();
});

{% for name,label,fg,bg in style_list %}
$("#hide{{ label }}").click(function(event){
    event.preventDefault();
    $("tr.{{ label }}").hide();
});
{% endfor %}
$("#hidenotfound").click(function(event){
    event.preventDefault();
    $("tr.not-found").hide();
});
