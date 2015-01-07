from django.conf.urls.defaults import patterns, include, url
from pythonfiddle.settings import DEBUG, PYTHON_LIB_DIR
from cloud_ide.shared.urls import urlpatterns as shared_urls

urlpatterns = shared_urls + patterns('cloud_ide.fiddle.views',
    url(r'^$', 'create', name='create_snippet'),
    url(r'^save/$', 'save', name='save_snippet'),
    url(r'^check_title/', 'check_title'),
    url(r'^tag_hint/$', 'tag_hint'),
    url(r'^(?P<snippet_slug>[-\w]+)/$', 'open', name='open_snippet'),
    url(r'^(?P<snippet_slug>[-\w]+)/embedded/$', 'open', {'embedded': True}),
)

urlpatterns += patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

if DEBUG:
    urlpatterns += patterns('', (
        r'^lib/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': PYTHON_LIB_DIR}
    ))