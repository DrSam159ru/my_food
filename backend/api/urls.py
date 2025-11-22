from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.urls import router as recipes_router
from users.urls import router as users_router


router = DefaultRouter()
router.registry.extend(recipes_router.registry)
router.registry.extend(users_router.registry)

urlpatterns = [
    path('', include(router.urls)),
]
