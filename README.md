python-pechkin
==============

Интеграция pechkin-mail.ru и вашего приложения

pechkin API: http://pechkin-mail.ru/?page=api

Пример кода

    from pechkin.api import PechkinApi

    api = PeckinApi('my_username', 'my_password')

    api.lists_get()  # Показывает все ваши базы

    list_id = api.lists_add('Первая База')

    plist = api.lists_get(list_id)

    plist.add_member(email='vsafronovich@gmail.com')

