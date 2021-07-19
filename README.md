## Установка и настройка

**1** Склонировать репозиторий командой
> **git@gitlab.4slovo.ru:4slovo.ru/qa_report_automation.git**
> 
**2** Создать config.json скопировав содержимое из config_template.json и добавить в него корпоративный логин\пароль пользователя. 
>   "USERNAME": "",
> 
>  "PASSWORD": ""

В дальнейшем планируется завести обезличенный аккаунт под сервис.

**3** Поднять контейнер с сервисом командой. 
> **docker-compose up -d**
>
Зайти на localhost:8000 и начать стартовую обработку текущих ближайших к релизу задач нажав кнопку.

## Установка и настройка
Проект создан в целях автоматизации отчетности отдельных задач и релизов.

На первом этапе реализован следующий функционал:

- Минимальный веб-интерфейс содержащий информацию по ближайшим релизам.
- Создание статьи с шаблоном отчета тестирования задачи при переходе задачи в статус Ready for QA.
- При нажатии кнопки в веб-интерфейсе производится проверка на условие готовности всех задач к релизу.
Если условие соблюдено, создается шаблон отчета по релизу, а так же все отчеты по задачам текущего релиза
  переносятся из папки с шаблонами в следующую существующую иерархию
    - Выпущеные релизы #Текущий год# 
        - Релиз #номер релиза# 
            - Задачи входящие в релиз.
