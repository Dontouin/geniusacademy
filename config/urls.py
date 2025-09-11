from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from django.views.static import serve

# --- Personnalisation admin ---
admin.site.site_header = "Genius Academy Admin"
admin.site.site_title = "Genius Academy Admin Portal"
admin.site.index_title = "Bienvenue dans Genius Academy"

# --- URL patterns principales (non traduites) ---
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("pwa/", include("pwa.urls")),  # si tu utilises django-pwa
]

# --- URL patterns traduites (i18n) ---
urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("", include("core.urls")),           # Pages principales multilingues
    path("accounts/", include("accounts.urls")),
    path("search/", include("search.urls")),
    # Ajouter d'autres apps si nécessaire :
    # path("programs/", include("course.urls")),
    # path("result/", include("result.urls")),
    # path("quiz/", include("quiz.urls")),
    # path("payments/", include("payments.urls")),
)

# --- Redirection racine vers langue par défaut (après i18n_patterns) ---
urlpatterns += [
    path("", RedirectView.as_view(url=f"/{settings.LANGUAGE_CODE}/", permanent=True)),
]

# --- Ajout du manifest et du service worker à la racine ---
urlpatterns += [
    path("manifest/site.webmanifest", serve, {
        "path": "manifest/site.webmanifest",
        "document_root": settings.STATIC_ROOT
    }),
    path("serviceworker.js", serve, {
        "path": "js/service-worker.js",
        "document_root": settings.STATIC_ROOT
    }),
]

# --- Fichiers statiques et media en DEBUG ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Pages d'erreur personnalisées
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page Not Found")}),
        path("500/", default_views.server_error),
    ]

# --- WhiteNoise static files ---
urlpatterns += staticfiles_urlpatterns()
