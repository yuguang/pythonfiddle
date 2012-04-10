from django.conf.urls.defaults import patterns, url
from pythonfiddle.settings import DEBUG, PYTHON_LIB_DIR
from cloud_ide.shared.urls import urlpatterns as shared_urls

urlpatterns = shared_urls + patterns('cloud_ide.fiddle.views',
    url(r'^$', 'create', name='create_snippet'),
    url(r'^save/$', 'save', name='save_snippet'),
    url(r'^check_title/', 'check_title'),
    url(r'^(?P<snippet_slug>[-\w]+)/$', 'open', name='open_snippet'),
    url(r'^(?P<snippet_slug>[-\w]+)/embedded/$', 'open', {'embedded': True}),
)

if DEBUG:
    urlpatterns += patterns('', (
        r'^lib/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': PYTHON_LIB_DIR}
    ))