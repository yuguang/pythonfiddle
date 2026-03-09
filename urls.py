from django.urls import re_path, include
from django.views.static import serve

from pythonfiddle.settings import DEBUG, PYTHON_LIB_DIR
from cloud_ide.shared.urls import urlpatterns as shared_urls
from cloud_ide.fiddle import views as fiddle_views

urlpatterns = shared_urls + [
    re_path(r'^$', fiddle_views.create, name='create_snippet'),
    re_path(r'^save/$', fiddle_views.save, name='save_snippet'),
    re_path(r'^check_title/', fiddle_views.check_title),
    re_path(r'^tag_hint/$', fiddle_views.tag_hint),
    re_path(r'^(?P<snippet_slug>[-\w]+)/$', fiddle_views.open, name='open_snippet'),
    re_path(r'^(?P<snippet_slug>[-\w]+)/embedded/$', fiddle_views.open, {'embedded': True}),
]

urlpatterns += [
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
]

if DEBUG:
    urlpatterns += [
        re_path(r'^lib/(?P<path>.*)$', serve, {'document_root': PYTHON_LIB_DIR}),
    ]
