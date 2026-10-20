from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, ProdutorViewSet, ProdutoViewSet, UnidadeMedidaViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("unidades", UnidadeMedidaViewSet, basename="unidade")
router.register("produtores", ProdutorViewSet, basename="produtor")
router.register("produtos", ProdutoViewSet, basename="produto")

urlpatterns = router.urls
