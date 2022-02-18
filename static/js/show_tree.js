function createDirectoryTree(url) {
    $.ajax({
        url: url,
        type: "get",
        dataType: "json",
        success: function (res) {
            if (res.status) {
                $.each(res.datas, function (k, v) {
                    let li = $("<li>" + v.title + "</li>").attr("id", "id_" + v.id)
                    let a = $("<a></a>").attr("href", "/project/" + v.project + "/wiki/" + v.id + "/show/").append(li)
                    if (v.parent == null) {
                        $("#tree").append(a).append($("<ul></ul>"))
                    } else {
                        $("#id_" + v.parent).parent().next().append(a).append($("<ul></ul>"))
                    }

                })
            } else {
                console.log("请求失败")
            }
        }
    })

}