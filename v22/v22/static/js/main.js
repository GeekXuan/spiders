$(document).ready(function () {
    var table = $('#table').DataTable({
        "dom": '<"row"<"col-md-4" l><"col-md-4 pull-right" <"ml-170"B>>>rtip',
        "DT_RowId": "row",
        "columns": [
            {"data": "id_"},
            {"data": "code"},
            {"data": "title"},
            {"data": "actor"},
            {"data": "type_"},
            {"data": "date_"},
            {"data": "score"},
            {"data": "director"},
            {"data": "producer"},
            {"data": "publisher"},
            {"data": "operation"},
        ],
        "lengthMenu": [[10, 20, 50], [10, 20, 50]],
        "language": {
            'loadingRecords': '加载中...',
            'processing': '查询中...',
            'search': '查询:',
            "lengthMenu": "每页 _MENU_ 条数据",
            "info": "共 _TOTAL_ 条数据，当前为第 _PAGE_ 页, 共 _PAGES_ 页",
            "infoEmpty": "没有数据",
            "emptyTable": "没有数据",
            "paginate": {
                "next": "下页",
                "previous": "上页"
            }
        },
        "ordering": false,
        "bServerSide": true,
        "bProcessing": true,
        "serverSide": true,
        "deferLoading": $("[name=def_count]").val(),//Only effective with "bServerSide"
        "ajax": {
            "url": "/find",
            "type": "GET",
            "data": $('#search_form').serializeObject(),
        }
    });
    table.ajax.reload().draw();
    /**点击搜索按钮**/
    $('#search_button').click(function () {
        let data = $('#search_form').serializeObject();
        console.log(data);
        table.context[0].ajax.data = data;
        table.search('', true, false).draw();
    });
});

/**将seralizeArray()返回结果改成通常的字典形式**/
jQuery.prototype.serializeObject = function () {
    var obj = new Object();
    $.each(this.serializeArray(), function (index, param) {
        if (!(param.name in obj)) {
            obj[param.name] = param.value;
        }
    });
    return obj;
};

