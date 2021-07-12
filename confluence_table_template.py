
def report_template(issue_key):
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
