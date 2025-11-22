from django.contrib import admin
from django.urls import include, path

from djoser.views import TokenCreateView, TokenDestroyView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/token/login/", TokenCreateView.as_view(),
         name="token-login"),
    path("api/auth/token/logout/", TokenDestroyView.as_view(),
         name="token-logout"),

    path("api/", include("api.urls")),
    path("api/", include("djoser.urls")),
    path("api/", include("djoser.urls.authtoken")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"),
         name="redoc"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"),
         name="swagger-ui"),

    path("s/", include("shortlinks.urls")),
]
