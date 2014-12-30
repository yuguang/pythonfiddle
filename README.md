Python Fiddle: the Python Cloud IDE
======================
An online editor and code sharing site for Python.

Getting the Code and Running it
-------------------------------

    git clone git://github.com/yuguang/pythonfiddle.git
    git clone git://github.com/yuguang/fiddlesalad.git
    git clone git://github.com/yuguang/cloud-ide-templates.git
    mv cloud-ide-templates templates
    git clone git://github.com/yuguang/django-cloud-ide.git
    cd django-cloud-ide
    python setup.py install
    cd ../pythonfiddle
    mv settings.default.py settings.py
    pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver

Read and follow the [Fiddle Salad documentation](https://github.com/yuguang/fiddlesalad#compiling-coffeescript) on compiling CoffeeScript.
Open http://127.0.0.1:8000/ in the browser.

Requirements
------------

* django >= 1.3.1
* django-mediasync >= 2.2.0
* django-social-auth >= 0.6.4
* django-taggit >= 0.9.3
* django-chunks >= 0.1

