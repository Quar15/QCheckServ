$(".list-group .item-header").click(function() {
    $(".list-group").removeClass("active");
    $(this).parent().addClass("active");
    $(".icon").text("+");
    $(this).children(".icon").text("-");
});

$(".list-group .item-header").last().click();