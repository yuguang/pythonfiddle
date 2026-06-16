"""
URL configuration for pythonfiddle_modern project.

Ported from legacy pythonfiddle/urls.py (Django 1.4) to Django 5.2 syntax.
See https://docs.djangoproject.com/en/5.2/topics/http/urls/ for details.
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Internationalisation (language switch form)
    path('i18n/', include('django.conf.urls.i18n')),

    # Social auth: OAuth login/callback/disconnect endpoints (replaces django-social-auth).
    # Provides: /social-auth/login/<backend>/, /social-auth/complete/<backend>/,
    #           /social-auth/disconnect/<backend>/  etc.
    # namespace='social' must match SOCIAL_AUTH_URL_NAMESPACE in settings.
    path('social-auth/', include('social_django.urls', namespace='social')),

    # Login page: renders a template with links to each social provider.
    # Phase 5 (URLs+Templates) will supply the real login.html template;
    # this TemplateView acts as a functional placeholder in the meantime.
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),

    # Logout: POST-only in Django 5 to prevent CSRF attacks.
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Core fiddle engine: create, save, check_title, tag_hint, open, embedded
    # Must come last so <snippet_slug> doesn't shadow the routes above.
    path('', include('cloud_ide.fiddle.urls')),
]
