from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, WidgetViewSet, FuenteDatosViewSet, 
    UsuarioWidgetViewSet, HistorialConsultaViewSet, DatoApiViewSet, DashboardWidgetView,
    HistorialFiltradoView, MiPanelView, GuardarPanelView
)
from .authentication import (
    RegistroView,
    ActivarDosFactorView,
    ConfirmarDosFactorView,
    VerificarLoginDosFactorView,
)

router = DefaultRouter()
router.register(r'widgets', WidgetViewSet, basename='widget')
router.register(r'fuentes', FuenteDatosViewSet, basename='fuente')
router.register(r'mis-widgets', UsuarioWidgetViewSet, basename='mi-widget')
router.register(r'historial-consultas', HistorialConsultaViewSet, basename='historial-consulta')
router.register(r'datos', DatoApiViewSet, basename='dato')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('dashboard/<int:id_widget>/', DashboardWidgetView.as_view(), name='dashboard-widget'),
    path('historial/', HistorialFiltradoView.as_view(), name='historial-filtrado'),
    path('mi-panel/', MiPanelView.as_view(), name='mi-panel'),
    path('mi-panel/guardar/', GuardarPanelView.as_view(), name='mi-panel-guardar'),
    # 2FA
    path('2fa/activar/', ActivarDosFactorView.as_view(), name='2fa-activar'),
    path('2fa/confirmar/', ConfirmarDosFactorView.as_view(), name='2fa-confirmar'),
    path('login/verificar-2fa/', VerificarLoginDosFactorView.as_view(), name='login-verificar-2fa'),
    path('', include(router.urls)),
]
