from rest_framework.routers import SimpleRouter

from .views import RequesterViewSet

router = SimpleRouter()
router.register("requesters", RequesterViewSet, basename="requester")

urlpatterns = router.urls
