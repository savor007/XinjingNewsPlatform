var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // load news category here
    $.ajax({
        url: "/loadcategory",
        type: "get",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno=="0") {
                // 刷新当前界面
                $(".menu fl").html('')
                for (var i = 0; i < resp.data.length; i++) {
                    category = resp.data[i]
                    console.log(String(category))
                    if (i==0)
                    {
                    li_data = '<li class="active" data-cid="' + category.id + '"><a href="javascript:;">' + category.name + '</a></li>'
                    }
                    else
                    {
                        li_data = '<li data-cid="' + category.id + '"><a href="javascript:;">' + category.name + '</a></li>'
                    }
                    $(".menu fl").append(li_data)
                }
            }
        }
    })


    //  update news list
    updateNewsData()
    // 首页分类切换


    $('.menu li').click(function () {
        var clickCid = Number($(this).attr('data-cid'))+Number(1)
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            //  判断页数，去更新新闻数据
            if (!data_querying)
            {
                data_querying=true
                if (cur_page<total_page){
                    cur_page+=1
                    updateNewsData()
                }
            }
        }
    })
})

function updateNewsData() {
    //  更新新闻数据
    var params={
        "cid":currentCid,
        "page":cur_page,
        "per_page":19
    }
    $.ajax({
        url: "/newslist",
        type: "get",
        contentType: "application/json",
        data:params,
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        //data=NewsPage_List, totalpage_num=total_page, current_page_num=current_page
        success: function (resp) {
            if (resp.errno=="0") {
                // 刷新当前界面
                total_page=resp.totalpage_num
                console.log("total pages="+String(total_page))
                if (cur_page==1){
                    $(".list_con").html('')
                }

                for (var i = 0; i < resp.data.length; i++) {
                    var news = resp.data[i]
                    var content = '<li>'
                    content += '<a href="/news/'+news.id+'" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                    content += '<a href="/news/'+news.id+'" class="news_title fl">' + news.title + '</a>'
                    content += '<a href="/news/'+news.id+'" class="news_detail fl">' + news.digest + '</a>'
                    content += '<div class="author_info fl">'
                    content += '<div class="source fl">来源：' + news.source + '</div>'
                    content += '<div class="time fl">' + news.create_time + '</div>'
                    content += '</div>'
                    content += '</li>'
                    $(".list_con").append(content)
                    }
                    data_querying=false
            }
        }
    })

}

