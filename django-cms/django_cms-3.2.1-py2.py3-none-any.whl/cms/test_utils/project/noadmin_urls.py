from django.views.i18n import javascript_catalog
from django.views.static import serve

from cms.utils.compat.dj import is_installed
from cms.utils.conf import get_cms_setting
from django.conf import settings
from django.conf.urls import include, url


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^media/cms/(?P<path>.*)$', serve,
        {'document_root': get_cms_setting('MEDIA_ROOT'), 'show_indexes': True}),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),
    url(r'^', include('cms.urls')),
]


if settings.DEBUG and is_installed('debug_toolbar'):
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
