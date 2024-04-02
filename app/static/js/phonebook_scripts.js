
onClickHeader = (event) => {  // обработка клика по одной из веток
    var accordion_item = $(event.target).parent().parent();
    var id = accordion_item.prop('id');
    var body = accordion_item.find('.accordion-body')
    if(!body.hasClass('.loaded')) {
        getData({get: id}, (response) => {
            buildAccordion('#' + body.prop('id'), response);
            body.addClass('.loaded');
        });  // запрос данных ветки из справочника если она не была ранее загружена
    }
}


buildAccordionBranch = (place_id, item_data) => {  // строим ветку (список подразделений)
    var accordion_item = $('<div>', {
        class: 'accordion-item branch',
        id: item_data.id
    });
    var accordion_header = $('<h4>', {
        class: 'accordion-header',
        id: 'heading-' + item_data.id
    });
    accordion_header.append(
        $('<button>', {
            text: item_data.title,
            type: 'button',
            class: 'accordion-button collapsed',
            'data-bs-toggle': 'collapse',
            'data-bs-target': '#collapse-' + item_data.id,
            'aria-expanded': 'false',
            'aria-controls': 'collapse-' + item_data.id
        }).on({
            click: onClickHeader
        })
    );
    accordion_item.append(accordion_header);
    var accordion_body = $('<div>', {
        id: 'collapse-' + item_data.id,
        class: 'accordion-collapse collapse',
        'aria-labelledby': 'heading-' + item_data.id
    });
    accordion_body.append(
        $('<div>', {
            id: 'accordion-body-' + item_data.id,
            class: 'accordion-body',
        })
    );
    accordion_item.append(accordion_body);
    accordion_item.appendTo(place_id);
}


buildAccordionLeaf = (place_id, item_data) => {  // строим лист (список абонентов)
    var accordion_item = $('<div>', {
        class: 'accordion-item leaf',
        id: item_data.id
    });
    var accordion_header = $('<h4>', {
        class: 'accordion-header',
    });
    accordion_header.append(
        $('<div>', {
            class: 'accordion-button collapsed',
            style: '--bs-accordion-btn-icon: none'
        }).append(
            '<table cellpadding="10px" width="100%" align="left">' +
                '<tr style="border: none">' +
                    '<td align="left" valign="center" width="15%" style="border-right: solid 1px #DEE2E6">' +
                        item_data.post +
                    '</td>' +
                    '<td align="left" valign="center" width="15%" style="border-right: solid 1px #DEE2E6">' +
                        item_data.surname + '<br>' + item_data.name + ' ' + item_data.patronymic +
                    '</td>' +
                    '<td align="center" valign="center" width="15%" style="border-right: solid 1px #DEE2E6">' +
                        item_data.rank +
                    '</td>' +
                    '<td align="center" valign="center" width="5%" style="border-right: solid 1px #DEE2E6">' +
                        item_data.extension.map((el) => el = el + '<br>').join('') +
                    '</td>' +
                    '<td align="center" valign="center" width="10%">' +
                        item_data.landline.map((el) => el = el + '<br>').join('') +
                    '</td>' +
                '</tr>' +
            '</table>'
        )
    );
    accordion_item.append(accordion_header);
    accordion_item.appendTo(place_id);
}


buildAccordion = (place_id, data) => {  // строим ветки и листья
    if(data) {
        if(data.abonents) {
            for(var i = 0; i < data.abonents.length; i++) {
                buildAccordionLeaf(place_id, data.abonents[i]);
            }
        }
        if(data.departments) {
            for(var i = 0; i < data.departments.length; i++) {
                buildAccordionBranch(place_id, data.departments[i]);
            }
        }
    }
}


show_tree = (tree) => {
    for(item in tree.departments) {
        accordion_item = $('#' + tree.departments[item].id + '.accordion-item.branch');
        body = accordion_item.find('.accordion-body');
        if(tree.show.departments.indexOf(tree.departments[item].id) != -1) {
            if(!body.hasClass('.loaded')) {  // если ветка не загружалась ранее
                // строим ветку и помечаем загруженной
                buildAccordion('#' + body.prop('id'), tree.departments[item]);
                body.addClass('.loaded');
            }
            // показываем нужную ветку
            accordion_item.children('.accordion-collapse').addClass('show');
            accordion_item.children().children('button').removeClass('collapsed');
            accordion_item.children().children('button').attr('aria-expanded', 'true');
            accordion_item.show();
            // остальные скрываем
            accordion_item.find('.accordion-item').hide();
        }
        show_tree(tree.departments[item]);  // переходим к следующей дочерней ветке
    }
    for(item in tree.abonents) {  // показываем абонентов
        if(tree.show.abonents.indexOf(tree.abonents[item].id) != -1) {
            accordion_item = $('#' + tree.abonents[item].id + '.accordion-item.leaf');
            accordion_item.show();
        }
    }
}


var old_search_str = '';
var timerId = null;

onKeyUpSearch = (event) => {  // нажатие на клавишу в input поле
    clearTimeout(timerId);
    timerId = setTimeout(() => {  // таймер, чтобы не сыпались запросы после нажатия каждой клавиши
        // если в течении 0,5 сек не было нажатий, то начинаем искать
        search_str = $(event.target).val();
        if((search_str.length >= 3) && (search_str != old_search_str)) {  // ищем только после ввода 3х символов
            getData({search: search_str}, (response) => {
                $('.accordion-item').hide();  // прячем все дерево
                show_tree(response);  // и рекурсивно отображаем пути к найденным абонентам
            });  // запрос на поиск
        } else if((old_search_str.length >= 3) && (search_str != old_search_str)) {
            // если в поле поиска меньше 3х символов, то показываем корень дерева
            accordion_item = $('.accordion-item');
            accordion_item.children('.accordion-collapse').removeClass('show');
            accordion_item.children().children('button').addClass('collapsed');
            accordion_item.children().children('button').attr('aria-expanded', 'false');
            accordion_item.show();
        }
        old_search_str = search_str;
    }, 500);
}


// request_type:
// 'get' - запрос конкретного подразделения, в качестве запроса указывается id подразделения
// 'search' - поиск по введенному значению, в качестве запроса указывается введенное значение
getData = (request, success, error = (jqXHR, exception) => {
        error_msg = '';
        if (jqXHR.status === 0) {
		    error_msg = 'Not connect. Verify Network.';
	    } else if (jqXHR.status == 404) {
		    error_msg = 'Requested page not found (404).';
	    } else if (jqXHR.status == 500) {
		    error_msg = 'Internal Server Error (500).';
	    } else if (exception === 'parsererror') {
		    error_msg = 'Requested JSON parse failed.';
	    } else if (exception === 'timeout') {
		    error_msg = 'Time out error.';
	    } else if (exception === 'abort') {
		    error_msg = 'Ajax request aborted.';
	    } else {
		    error_msg = 'Uncaught Error. ' + jqXHR.responseText;
	    }
        $('#error-msg').text(error_msg);
        $('#error-msg').css({'visibility': 'visible'});
    }) => {  // ajax запрос к серверу
    $.ajax({
        type: 'GET',
        url: 'phonebook/get_data',
        async: true,
        dataType: 'json',
        data: request,
        success: success,
        error: error
    });
}


$(document).keyup(() => {  // при нажатии клавиши Esc в любом месте документа
        if(event.keyCode == 27) {  // сбросить строку поиска и закрыть все узлы телефонной книги
            $('#phonebook_search').val('');
            search_str = '';
            old_search_str = '';
            accordion_item = $('.accordion-item');
            accordion_item.children('.accordion-collapse').removeClass('show');
            accordion_item.children().children('button').addClass('collapsed');
            accordion_item.children().children('button').attr('aria-expanded', 'false');
            accordion_item.show();
        }
    }
);


$(document).ready(() => {
    getData({get: '0'}, (response) => {  // загружаем корень
        buildAccordion('#phonebook_list', response);
    });
    $('#phonebook_search').focus();
    $('#phonebook_search').keyup(onKeyUpSearch);
});
