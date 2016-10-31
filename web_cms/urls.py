from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from mezzanine.core.views import direct_to_template


admin.autodiscover()

urlpatterns = i18n_patterns("",
    ("^admin/", include(admin.site.urls)),
)

urlpatterns += patterns(
    '',
    url("^$", direct_to_template, {"template": "index.html"}, name="home"),
    url("^metadata/?.*", staff_member_required(direct_to_template), 
        {"template": "mibc_api/metadata.html"}, name="metadata"),
    url("^samplemeta/?.*", staff_member_required(direct_to_template), 
        {"template": "mibc_api/samplemeta.html"}, name="samplemeta"),
    url("^validator/?.*", staff_member_required(direct_to_template), 
        {"template": "mibc_api/validator.html"}, name="validator"),

    url("^tickets/", include("knowledge.urls")),
    url("^files/", include("cloud_browser.urls")),
    url("^api/", include("mibc_api.urls")),

    # MEZZANINE'S URLS
    # ----------------
    # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!

    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.
    ("^", include("mezzanine.urls")),

)

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
