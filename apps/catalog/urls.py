from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, DepartmentViewSet, PriorityViewSet

router = SimpleRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("categories", CategoryViewSet, basename="category")
router.register("priorities", PriorityViewSet, basename="priority")

urlpatterns = router.urls
