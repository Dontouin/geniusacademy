from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# --- Personnalisation du panneau admin ---
admin.site.site_header = "SkyLearn Admin"
admin.site.site_title = "SkyLearn Admin Portal"
admin.site.index_title = "Bienvenue sur SkyLearn Admin"

# --- URL patterns principales (non traduites) ---
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

# --- URL patterns avec traduction (i18n) ---
urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("", include("core.urls")),
    path("jet/", include("jet.urls", "jet")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("accounts/", include("accounts.urls")),
    path("search/", include("search.urls")),
    # Décommenter si besoin
    # path("programs/", include("course.urls")),
    # path("result/", include("result.urls")),
    # path("quiz/", include("quiz.urls")),
    # path("payments/", include("payments.urls")),
)

# --- Fichiers statiques et media ---
# En production (DEBUG=False), WhiteNoise servira automatiquement STATIC_ROOT
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# --- Pages d'erreur personnalisées pour tests en mode DEBUG ---
if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page Not Found")},
        ),
        path("500/", default_views.server_error),
    ]

urlpatterns +=staticfiles_urlpatterns()