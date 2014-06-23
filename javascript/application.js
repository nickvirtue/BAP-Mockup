
$(function() {

        var str=location.href.toLowerCase();
        $(".navbar-nav li a").each(function() {
            if (str.indexOf(this.href.toLowerCase()) > -1) {
                $("li").removeClass("active");
                $(this).parent().addClass("active");
            }
        });


});