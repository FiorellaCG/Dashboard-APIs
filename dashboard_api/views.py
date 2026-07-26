from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import bcrypt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Autenticacion2FA

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo')
        password = request.data.get('password')

        if not correo or not password:
            return Response({'error': 'Por favor provea correo y password.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verificar password con bcrypt
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
                return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({'error': 'Error verificando la contraseña.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if usuario.estado != 'activo':
            return Response({'error': 'Usuario inactivo o bloqueado.'}, status=status.HTTP_403_FORBIDDEN)

        # Verificar si el usuario tiene 2FA activo y verificado
        tiene_2fa = Autenticacion2FA.objects.filter(
            id_usuario=usuario, verificado=True
        ).exists()

        if tiene_2fa:
            # No emitir tokens todavía; el frontend debe pedir el código TOTP
            return Response(
                {'requiere_2fa': True, 'correo': usuario.correo},
                status=status.HTTP_200_OK
            )

        # Sin 2FA: generar y retornar tokens normalmente
        refresh = RefreshToken()
        refresh['user_id'] = usuario.id_usuario
        refresh['correo'] = usuario.correo

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'usuario': {
                'id': usuario.id_usuario,
                'nombre': usuario.nombre,
                'correo': usuario.correo,
                'rol': usuario.id_rol.nombre if usuario.id_rol else None
            }
        }, status=status.HTTP_200_OK)

from rest_framework import viewsets
from .models import Widget, FuenteDatos, UsuarioWidget, HistorialConsulta, DatoApi
from .serializers import WidgetSerializer, FuenteDatosSerializer, UsuarioWidgetSerializer, HistorialConsultaSerializer, DatoApiSerializer

class WidgetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer

class FuenteDatosViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FuenteDatos.objects.all()
    serializer_class = FuenteDatosSerializer

class UsuarioWidgetViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioWidgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UsuarioWidget.objects.filter(id_usuario=self.request.user.id_usuario)

    def perform_create(self, serializer):
        serializer.save(id_usuario=self.request.user)

class HistorialConsultaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialConsulta.objects.all()
    serializer_class = HistorialConsultaSerializer

class DatoApiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DatoApi.objects.all()
    serializer_class = DatoApiSerializer

from django.utils import timezone
from datetime import timedelta
from .services.apis_externas import fetch_world_bank_data, fetch_openweather_data, fetch_restcountries_data

class DashboardWidgetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_widget):
        try:
            widget = Widget.objects.select_related('id_fuente').get(id_widget=id_widget)
        except Widget.DoesNotExist:
            return Response({'error': 'Widget no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        fuente = widget.id_fuente
        if not fuente:
            return Response({'error': 'Widget no tiene fuente de datos asociada.'}, status=status.HTTP_400_BAD_REQUEST)

        pais = request.query_params.get('pais')

        # Revisar caché: datos de esta fuente (podríamos filtrar más por usuario o parámetros, pero para el ejemplo usamos fuente)
        hace_6_horas = timezone.now() - timedelta(hours=6)
        
        filtros_cache = {
            'fuente': fuente.nombre,
            'fecha_consulta__gte': hace_6_horas
        }
        if pais:
            filtros_cache['pais'] = pais

        dato_cache = DatoApi.objects.filter(**filtros_cache).order_by('-fecha_consulta').first()

        if dato_cache:
            return Response({
                'origen': 'cache',
                'datos': {
                    'valor': dato_cache.valor,
                    'unidad': dato_cache.unidad,
                    'fecha_dato': dato_cache.fecha_dato,
                    'pais': dato_cache.pais
                }
            })

        # Si no hay caché, llamar a la API externa
        resultado = None
        if 'world bank' in fuente.nombre.lower():
            resultado = fetch_world_bank_data(request.user, fuente, country_code=pais) if pais else fetch_world_bank_data(request.user, fuente)
        elif 'openweather' in fuente.nombre.lower():
            resultado = fetch_openweather_data(request.user, fuente, city=pais) if pais else fetch_openweather_data(request.user, fuente)
        elif 'rest countries' in fuente.nombre.lower():
            resultado = fetch_restcountries_data(request.user, fuente, country_name=pais) if pais else fetch_restcountries_data(request.user, fuente)
        else:
            return Response({'error': 'Fuente de datos no soportada.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'error' in resultado:
            return Response({'error': resultado['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'origen': 'api',
            'datos': resultado
        })


