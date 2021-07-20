def issue_report_template(issue_key):
    table = '<table class="relative-table tablesorter tablesorter-default stickyTableHeaders confluenceTable" style="width: 68.4398%">' \
            '<colgroup>' \
            '<col style="width: 17.0561%"></col>' \
            '<col style="width: 42.7652%"></col>' \
            '<col style="width: 20.4488%"></col>' \
            '<col style="width: 19.7205%"></col>' \
            '</colgroup>' \
            '<thead class="tableFloatingHeaderOriginal">' \
            '<tr class="tablesorter-headerRow">' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">Номер задачи</div></th><th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>1 Итерация</p>' \
            '<p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>2 Итерация</p>' \
            '<p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>3 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '</tr>' \
            '</thead>' \
            '<thead class="tableFloatingHeader" style="display: none">' \
            '<tr class="tablesorter-headerRow"><th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">Номер задачи</div>' \
            '</th>' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>1 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>2 Итерация</p>' \
            '<p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '<th class="tablesorter-header sortableHeader tablesorter-headerUnSorted confluenceTh" scope="col">' \
            '<div class="tablesorter-header-inner">' \
            '<p>3 Итерация</p>' \
            '<p>Исполнитель / Дата / Тестовая среда</p>' \
            '<p>Кейсы</p>' \
            '</div>' \
            '</th>' \
            '</tr>' \
            '</thead>' \
            '<tbody>' \
            '<tr>' \
            '<td class="confluenceTd"><div class="content-wrapper">' \
            f'<p><a href="https://jira.4slovo.ru/browse/{issue_key}" class="">https://jira.4slovo.ru/browse/{issue_key}</a></p>' \
            '</div>' \
            '</td>' \
            '<td class="confluenceTd"><div class="content-wrapper" title=""><p><br></br></p>' \
            '</div>' \
            '</td>' \
            '<td class="confluenceTd"><br></br></td><td class="confluenceTd"><br></br></td></tr></tbody></table>'
    return table


def release_report_template(country):
    checklist_link = None
    if country == 'ru':
        checklist_link = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId=37127178'
    elif country == 'kz':
        checklist_link = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId=40370935'
    elif country == 'ge':
        checklist_link = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId=47383257'
    template = '<p class="auto-cursor-target">' \
               f'<a href="{checklist_link}">Чеклист тестирования релиза {country}</a>' \
               '</p>' \
               '<table border="1" class="confluenceTable">' \
               '<colgroup><col></col><col></col><col></col></colgroup>' \
               '<tbody>' \
               '<tr>' \
               '<th class="confluenceTh"><br></br></th><th class="confluenceTh">RC Исполнитель, дата</th>' \
               '<th colspan="1" class="confluenceTh">Staging <span>Исполнитель, дата</span></th>' \
               '</tr>' \
               '<tr>' \
               '<td class="confluenceTd"><h2>Регресс десктопной версии</h2></td><td class="confluenceTd">' \
               '<div class="content-wrapper"></div></td><td colspan="1" class="confluenceTd"><br></br>' \
               '</td>' \
               '</tr>' \
               '<tr>' \
               '<td class="confluenceTd"><h2><span>Регресс мобильной версии</span></h2></td>' \
               '<td class="confluenceTd"><br></br></td><td colspan="1" class="confluenceTd"><br></br>' \
               '</td>' \
               '</tr>' \
               '<tr>' \
               '<td class="confluenceTd"><h2>Исследовательское тестирование</h2></td>' \
               '<td class="confluenceTd"><br></br></td><td colspan="1" class="confluenceTd">' \
               '<br></br>' \
               '</td>' \
               '</tr>' \
               '</tbody>' \
               '</table>'
    return template
