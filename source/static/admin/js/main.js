$(function() {

    // 打开登录框


    // 点击输入框，提示文字上移
    // $('.form_group').on('click focusin',function(){

    // 登录框和注册框切换

    //  登录表单提交

    //  注册按钮点击

})

//logout function
function logout() {
    $.ajax({
        url: "/admin/logout",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            // 刷新当前界面
        }
    })


}

