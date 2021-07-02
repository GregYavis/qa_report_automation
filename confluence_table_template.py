table1 = '<a href="#page-metadata-start" class="assistive">Переход к началу метаданных</a>' \
        '<div id="page-metadata-end" class="assistive"></div>' \
        '<div id="main-content" class="wiki-content">' \
        '<div class="table-wrap"><table class="relative-table confluenceTable" style="width: 76.313%;">' \
        '<colgroup>' \
        '<col style="width: 12.9977%;"/>' \
        '<col style="width: 41.3115%;"/>' \
        '<col style="width: 15.5269%;"/>' \
        '<col style="width: 15.0351%;"/>' \
        '</colgroup><tbody>' \
        '<tr>' \
        '<th class="confluenceTh">Номер задачи</th>' \
        '<th class="confluenceTh"><p>1 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></th>' \
        '<th class="confluenceTh"><p>2 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></th>' \
        '<th class="confluenceTh"><p>3 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></th>' \
        '</tr>' \
        '<tr>' \
        '<td class="confluenceTd">' \
        '<div class="content-wrapper"><p><br/></p></div></td>' \
        '<td class="confluenceTd">' \
        '<div class="content-wrapper" title="">' \
        '<p><br/></p></div></td>' \
        '<td class="confluenceTd"><br/></td>' \
        '<td class="confluenceTd"><br/></td></tr></tbody></table></div></div>'


def confluence_body_template(issue_key, issue_status, issue_url, issue_summary):
    table = '<div id="main-content" class="wiki-content">' \
            '<div class="table-wrap"><table class="relative-table confluenceTable tablesorter tablesorter-default stickyTableHeaders" style="width: 76.313%; padding: 0px;" role="grid" resolved="">' \
            '<colgroup>' \
            '<col style="width: 12.9977%;"></col>' \
            '<col style="width: 41.3115%;"></col>' \
            '<col style="width: 15.5269%;"></col>' \
            '<col style="width: 15.0351%;"></col>' \
            '</colgroup>' \
            '<thead class="tableFloatingHeaderOriginal"><tr role="row" class="tablesorter-headerRow">' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="0" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="Номер задачи: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner">Номер задачи</div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="1" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="1 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>1 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="2" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="2 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>2 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="3" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="3 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>3 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '</tr>' \
            '</thead>' \
            '<thead class="tableFloatingHeader" style="display: none;">' \
            '<tr role="row" class="tablesorter-headerRow">' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="0" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="Номер задачи: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner">Номер задачи</div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="1" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="1 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>1 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="2" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="2 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>2 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '<th class="confluenceTh tablesorter-header sortableHeader tablesorter-headerUnSorted" data-column="3" tabindex="0" scope="col" role="columnheader" aria-disabled="false" unselectable="on" aria-sort="none" aria-label="3 ИтерацияИсполнитель / Дата / Тестовая средаКейсы: No sort applied, activate to apply an ascending sort" style="user-select: none;">' \
            '<div class="tablesorter-header-inner"><p>3 Итерация</p><p>Исполнитель / Дата / Тестовая среда</p><p>Кейсы</p></div></th>' \
            '</tr>' \
            '</thead>' \
            '<tbody aria-live="polite" aria-relevant="all">' \
            '<tr role="row"><td class="confluenceTd"><div class="content-wrapper">' \
            '<p>' \
            f'<span class="jira-issue" data-jira-key="{issue_key}">' \
            f'<a href="{issue_url}" class="jira-issue-key external-link" target="_blank" data-ext-link-init="true"><img class="icon" src="https://jira.4slovo.ru/secure/viewavatar?size=xsmall&amp;avatarId=10303&amp;avatarType=issuetype"></img>{issue_key}</a>' \
            '-' \
            f'<span class="summary">{issue_summary}</span>' \
            '<span class="aui-lozenge aui-lozenge-subtle             aui-lozenge-default' \
            f'jira-macro-single-issue-export-pdf">{issue_status}</span>' \
            '</span></p>' \
            '</div></td>' \
            '<td class="confluenceTd">' \
            '<div class="content-wrapper" title="">' \
            '<p><br></br></p></div></td>' \
            '<td class="confluenceTd"><br></br></td>' \
            '<td class="confluenceTd"><br></br></td></tr></tbody></table></div></div>'
    return table
