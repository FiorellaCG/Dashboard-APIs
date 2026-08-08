from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import bcrypt
import json
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Autenticacion2FA
from .services.bitacora_service import registrar_bitacora

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

        registrar_bitacora(
            usuario=usuario,
            codigo='001',
            descripcion=f"Inicio de sesion: {usuario.correo}",
            request=request
        )

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
from rest_framework.decorators import action
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
        registrar_bitacora(
            usuario=self.request.user,
            codigo='002',
            descripcion="Modificacion de configuracion de widget",
            request=self.request
        )

    def perform_update(self, serializer):
        serializer.save()
        registrar_bitacora(
            usuario=self.request.user,
            codigo='002',
            descripcion="Modificacion de configuracion de widget",
            request=self.request
        )

    def perform_destroy(self, instance):
        instance.delete()
        registrar_bitacora(
            usuario=self.request.user,
            codigo='004',
            descripcion="Eliminacion de widget del panel",
            request=self.request
        )

    @action(detail=False, methods=['post'], url_path=r'guardar/(?P<id_widget>[^/.]+)')
    def get_or_create_config(self, request, id_widget=None):
        defaults = {}
        for field in ['visible', 'orden', 'configuracion']:
            if field in request.data:
                defaults[field] = request.data[field]

        obj, created = UsuarioWidget.objects.update_or_create(
            id_usuario=request.user,
            id_widget_id=id_widget,
            defaults=defaults
        )

        registrar_bitacora(
            usuario=request.user,
            codigo='002',
            descripcion="Modificacion de configuracion de widget",
            request=request
        )

        serializer = self.get_serializer(obj)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

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

        registrar_bitacora(
            usuario=request.user,
            codigo='003',
            descripcion=f"Consulta widget {id_widget}, pais={pais}",
            request=request
        )

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


from django.db.models import Q, Avg, Sum, Count, Max, Min

class HistorialFiltradoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Registrar bitácora (Código 003: Consulta de información)
        registrar_bitacora(
            usuario=request.user,
            codigo='003',
            descripcion="Consulta de historico con filtros",
            request=request
        )

        queryset = DatoApi.objects.all()

        # 2. Capturar query params
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        categoria = request.query_params.get('categoria')
        palabra_clave = request.query_params.get('palabra_clave')

        # 3. Aplicar filtros dinámicos
        if fecha_inicio:
            queryset = queryset.filter(fecha_dato__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_dato__lte=fecha_fin)
        if categoria:
            queryset = queryset.filter(id_consulta__categoria__iexact=categoria)
        if palabra_clave:
            queryset = queryset.filter(
                Q(pais__icontains=palabra_clave) | Q(indicador__icontains=palabra_clave)
            )

        # Ordenar y limitar a 200 por rendimiento
        queryset_ordenado = queryset.order_by('-fecha_consulta')[:200]

        # Serializar resultados
        serializer = DatoApiSerializer(queryset_ordenado, many=True)
        resultados_data = serializer.data

        # 4. Calcular estadísticas agrupadas por unidad sobre el queryset filtrado
        estadisticas = []
        if queryset.exists():
            grupos = (
                queryset.values('unidad')
                .annotate(
                    promedio=Avg('valor'),
                    total=Sum('valor'),
                    cantidad=Count('id_dato'),
                    val_max=Max('valor'),
                    val_min=Min('valor')
                )
            )

            for g in grupos:
                unid = g['unidad']
                qs_grupo = queryset.filter(unidad=unid)

                max_obj = qs_grupo.order_by('-valor').first()
                min_obj = qs_grupo.order_by('valor').first()

                estadisticas.append({
                    'unidad': unid,
                    'promedio': round(g['promedio'], 2) if g['promedio'] is not None else 0,
                    'total': round(g['total'], 2) if g['total'] is not None else 0,
                    'cantidad': g['cantidad'],
                    'pais_max': {
                        'pais': max_obj.pais if max_obj else None,
                        'valor': max_obj.valor if max_obj else None
                    },
                    'pais_min': {
                        'pais': min_obj.pais if min_obj else None,
                        'valor': min_obj.valor if min_obj else None
                    }
                })

        return Response({
            'resultados': resultados_data,
            'total_resultados': len(resultados_data),
            'estadisticas': estadisticas
        }, status=status.HTTP_200_OK)


class MiPanelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        widgets_activos = Widget.objects.filter(activo=True)
        user_configs = {
            uw.id_widget_id: uw
            for uw in UsuarioWidget.objects.filter(id_usuario=request.user)
        }

        resultado = []
        for w in widgets_activos:
            uw = user_configs.get(w.id_widget)
            if uw:
                visible = uw.visible
                orden = uw.orden if uw.orden is not None else 0
                config_raw = uw.configuracion
                config_parsed = None
                if config_raw:
                    try:
                        config_parsed = json.loads(config_raw) if isinstance(config_raw, str) else config_raw
                    except Exception:
                        config_parsed = None
                
                tipo_custom = None
                if isinstance(config_parsed, dict):
                    tipo_custom = config_parsed.get('tipo_grafico')
                
                tipo_grafico_personalizado = tipo_custom if tipo_custom else w.tipo_grafico
            else:
                visible = True
                orden = 0
                config_parsed = None
                tipo_grafico_personalizado = w.tipo_grafico

            resultado.append({
                'id_widget': w.id_widget,
                'nombre': w.nombre,
                'tipo_grafico_original': w.tipo_grafico,
                'visible': visible,
                'orden': orden,
                'tipo_grafico_personalizado': tipo_grafico_personalizado,
                'configuracion': config_parsed
            })

        resultado.sort(key=lambda x: x['orden'])
        return Response(resultado, status=status.HTTP_200_OK)


class GuardarPanelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        widgets_data = request.data.get('widgets', [])
        if not isinstance(widgets_data, list):
            return Response({'error': 'Formato inválido. Se esperaba una lista en "widgets".'}, status=status.HTTP_400_BAD_REQUEST)

        for item in widgets_data:
            id_widget = item.get('id_widget')
            if not id_widget:
                continue

            visible = item.get('visible', True)
            orden = item.get('orden', 0)
            tipo_grafico = item.get('tipo_grafico')

            # Recuperar o inicializar dict de configuracion
            uw = UsuarioWidget.objects.filter(id_usuario=request.user, id_widget_id=id_widget).first()
            current_config = {}
            if uw and uw.configuracion:
                try:
                    parsed = json.loads(uw.configuracion) if isinstance(uw.configuracion, str) else uw.configuracion
                    if isinstance(parsed, dict):
                        current_config = parsed
                except Exception:
                    current_config = {}

            if tipo_grafico is not None:
                current_config['tipo_grafico'] = tipo_grafico

            UsuarioWidget.objects.update_or_create(
                id_usuario=request.user,
                id_widget_id=id_widget,
                defaults={
                    'visible': visible,
                    'orden': orden,
                    'configuracion': json.dumps(current_config)
                }
            )

        registrar_bitacora(
            usuario=request.user,
            codigo='002',
            descripcion="Actualizacion de panel personalizado",
            request=request
        )

        return Response({'mensaje': 'Panel personalizado actualizado correctamente.'}, status=status.HTTP_200_OK)




