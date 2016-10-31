"""Cloud browser URLs."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from cloud_browser.app_settings import settings

urlpatterns = patterns(
    'cloud_browser.views',  # pylint: disable=C0103
    url(r'^$', RedirectView.as_view(url="browser"), 
        name="cloud_browser_index",),
    url(r'^browser/(?P<path>.*)$', 'browser', name="cloud_browser_browser"),
    url(r'^document/(?P<path>.*)$', 'document', name="cloud_browser_document"),
)

if settings.app_media_url is None:
    # Use a static serve.
    urlpatterns += patterns('',  # pylint: disable=C0103
        url(r'^app_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.app_media_doc_root},
            name="cloud_browser_media"),
    )
