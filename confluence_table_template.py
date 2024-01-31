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
    template = (f'<table class="wrapped confluenceTable stickyTableHeaders tablesorter tablesorter-default" resolved="" style="padding: 0px;" role="grid">'
                f'<thead class="tableFloatingHeaderOriginal">'
                f'<tr role="row" class="tablesorter-headerRow">'
                f'<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="0" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label=": No sort applied, activate to apply an ascending sort" style="user-select: none;">'
                f'<div class="tablesorter-header-inner"><br></br></div>'
                f'</th><th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="1" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="RC исполнитель, дата(моб. можно в эмуляторе): No sort applied, activate to apply an ascending sort" style="user-select: none;">'
                f'<div class="tablesorter-header-inner">RC исполнитель, дата<h6>(моб. можно в эмуляторе)</h6>'
                f'</div></th><th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="2" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="Staging исполнитель, дата: No sort applied, activate to apply an ascending sort" style="user-select: none;">'
                f'<div class="tablesorter-header-inner">Staging исполнитель, дата'
                f'</div></th></tr></thead>'
                f'<thead class="tableFloatingHeader" style="display: none;">'
                f'<tr role="row" class="tablesorter-headerRow"><th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="0" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label=": No sort applied, activate to apply an ascending sort" style="user-select: none;">'
                f'<div class="tablesorter-header-inner"><br></br></div></th><th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="1" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="RC исполнитель, дата(моб. можно в эмуляторе): No sort applied, activate to apply an ascending sort" style="user-select: none;">'
                f'<div class="tablesorter-header-inner">RC исполнитель, дата<h6>(моб. можно в эмуляторе)'
                f'</h6></div></th><th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="2" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="Staging исполнитель, дата: No sort applied, activate to apply an ascending sort" style="user-select: none;"><div class="tablesorter-header-inner">Staging исполнитель, дата'
                f'</div></th></tr></thead><colgroup><col><col><col></col></col></col></colgroup><tbody aria-live="polite" aria-relevant="all">'
                f'<tr role="row">'
                f'<td class="confluenceTd">'
                f'<h2>Проверка деплой лога</h2></td><td class="highlight-grey confluenceTd" title="Background color : " data-highlight-colour="grey">'
                f'<br></br></td><td class="confluenceTd"><br></br></td></tr><tr role="row"><td class="confluenceTd"><h2>Проверка логов до и&nbsp;после релиза</h2><h2>на наличие Warning, Error</h2></td><td class="highlight-grey confluenceTd" title="Background color : " data-highlight-colour="grey">'
                f'<br></br></td><td class="confluenceTd"><br></br></td></tr><tr role="row"><td class="confluenceTd"><h2>Регресс десктопной версии</h2></td><td class="confluenceTd">'
                f'<br></br></td><td class="confluenceTd"><br></br></td></tr><tr role="row"><td class="confluenceTd"><h2>Регресс мобильной версии</h2></td><td class="confluenceTd">'
                f'<br></br></td><td class="confluenceTd"><br></br></td></tr><tr role="row"><td class="confluenceTd"><h2>Исследовательское тестирование</h2></td><td class="confluenceTd">'
                f'<br></br></td><td class="confluenceTd"><br></br></td></tr></tbody></table>')
    return template
