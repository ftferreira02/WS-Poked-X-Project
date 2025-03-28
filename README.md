# WS-Poked-X-Project

how to run: 

```
“python manage.py runserver”
e abrir o browser com a URL: http://localhost:8000
```



Estrutura do Projeto Django

```
webproj/ ------ Pasta para o projeto. Pode ter qualquer nome.
manage.py -- Utilitário em commando de linha para interagir com o projeto.
webproj/ --- Pacote do projeto. Nome usado para imports
    __init__.py --- Ficheiro que define esta pasta como um pacote, em Python.
    settings.py --- Configurações do projeto Django.
    urls.py ------- Mapping/routing das URLs para este projeto.
    wsgi.py ------- Um ponto de entrada para webservers compatíveis com WSGI.
app/ ------- Aplicação web individual, podendo coexistir várias.\
    templates/ ---- Ficheiros HTML, invocados pelas views.
    static/ ------- CSS, JS, imagens, etc. – configurável em “settings.py”
    __init__.py --
    views/ ------ Recebe os pedidos dos clientes e devolve as respostas.
        fight/
            fight_view.py
        search/
            search_view.py
        stats/
            stats_view.py
    models/ --- Modelos dos dados.
        fight/
            fight_view.py
        search/
            search_view.py
        stats/
            stats_view.py
    admin.py ------ Criação automática de interface para o modelo de dados.
    forms.py ------ Permite a receção de dados enviados pelos clients.

```