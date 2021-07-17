$(document).ready( function () {
    var $ = django.jQuery;
    var url_pic = '';
    var random_name_sup = '';
    var session_web = '';
    $("#text_captcha").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#res_captcha").click();
        }
    });
    $("#req_captcha").on('click',function() {
        $(".info").css("display","none");
        $('.form-response').css("display","none");
        var queryURL = 'GetCaptcha/';
        random_name_sup = $("#rnd_name_sup").val();
        console.log(random_name_sup);
        // return true
        if(rnd_name_sup != ''){
            $(this).prop("disabled",true);
            var data = {"rnd_name_sup": random_name_sup};
            $.ajax({
                url: queryURL,
                type: 'get',
                data,
                contentType: 'application/json',
                success: function(response){
                    if (response.status){
                        $(this).prop("disabled",false);
                        $("#res_captcha").prop("disabled",false);
                        url_pic = response.url_pic;
                        session_web = response.session_web
                        url = "http://185.201.49.52:8080/static/admin/sepehr/supplier/captcha/" + response.url_pic;
                        $("#img_captcha").attr("src",url);
                        $("#img_captcha").show(); // Display image element
                        $('.form-request').css("display","none");
                        $('.form-response').css("display","block");
                        $("#text_captcha").focus();
                    }
                    else{
                        $(this).prop("disabled",false);
                        $("#res_captcha").prop("disabled",false);
                        $(".info strong").text(response.message);
                        $(".info").css("display","block");
                        $("#req_captcha").focus();
                    }
                },
                error: function(xhr) {
                    $(this).prop("disabled",false);
                    $("#res_captcha").prop("disabled",false);
                    $(".info strong").text("Error: " + xhr.text);
                    $(".info").css("display","block");
                }
            });
        }else{
            $(".info strong").text("Error: name supplier is empty");
            $(".info").css("display","block");
        }

    });

    $("#res_captcha").on('click',function() {
        $(".info").css("display","none");
        $(this).prop("disabled",true);
        var queryURL = 'SetCaptcha/';
        data = {
            txtCaptchaNumber: $("#text_captcha").val(),
            url_pic: url_pic,
            rnd_name_sup: random_name_sup,
            session_web: session_web
        }
        if(rnd_name_sup != ''){
            $.ajax({
                url: queryURL,
                type: 'get',
                data,
                success: function(response){
                    $("#text_captcha").val('');
                    if (response.status == true){
                        let name_sup = response.name_sup;
                        let credit = response.credit;
                        $(this).prop("disabled",false);
                        $("#req_captcha").prop("disabled",false);
                        $(".info strong").text("Success");
                        $(".info").css("display","block");
                        $('.form-response').css("display","none");
                        $('.form-request').css("display","block");
                        $('#result_list tbody th a').each(function() {
                            if ($(this).text().indexOf(name_sup) > -1) {
                                $(this).parents(".field-alias_name").nextAll(".field-credit").html(credit);
                                $(this).parents(".field-alias_name").nextAll(".field-status").children("img").attr("alt","True");
                                $(this).parents(".field-alias_name").nextAll(".field-status").children("img").attr("src","/static/admin/img/icon-yes.svg");
                                return false;
                            }
                        });
                    }
                    else if (response.type === 'supplier' || response.type === 'credit') {
                        $(this).prop("disabled",false);
                        $("#req_captcha").prop("disabled",false);
                        $(".info strong").text("Problem: " + response.text);
                        $('.form-response').css("display","none");
                        $('.form-request').css("display","block");
                        $(".info").css("display","block");
                    }
                    else{
                        $("#text_captcha").val('');
                        $("#res_captcha").prop("disabled",false);
                        $("#req_captcha").prop("disabled",false);
                        $(".info strong").text("Error: " + response.text);
                        session_web = response.session_web;
                        $(".info").css("display","block");
                        let url = "http://185.201.49.52:8080/static/admin/sepehr/supplier/captcha/" + response.url_pic;
                        $("#img_captcha").attr("src",url);
                        $("#text_captcha").focus();
                    }
                },
                error: function(xhr) {
                    $("#text_captcha").val('');
                    $(this).prop("disabled",false);
                    $("#req_captcha").prop("disabled",false);
                    $(".info strong").text("Error: " + xhr.text);
                    $(".info").css("display","block");
                }
            });
        }else{
            $(".info strong").text("Error: captcha is empty");
            $(".info").css("display","block");
            $("#text_captcha").focus();
        }
    });
});