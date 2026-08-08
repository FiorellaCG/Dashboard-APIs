from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
import bcrypt
from .models import Usuario, Rol
from .services.bitacora_service import registrar_bitacora

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token no contiene identificador de usuario', code='token_not_valid')

        try:
            user = Usuario.objects.get(id_usuario=user_id)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado', code='user_not_found')

        if user.estado != 'activo':
            raise AuthenticationFailed('Usuario inactivo', code='user_inactive')

        # Para que DRF funcione bien, le agregamos la propiedad is_authenticated (simulando auth.User)
        user.is_authenticated = True
        return user

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from .models import Autenticacion2FA
from .services.totp_service import (
    generar_secreto, generar_qr_uri, generar_qr_base64, verificar_codigo
)


# ---------------------------------------------------------------------------
# Helpers para generar tokens JWT (reutilizado en LoginView y VerificarLogin)
# ---------------------------------------------------------------------------
def _generar_tokens(usuario):
    refresh = RefreshToken()
    refresh['user_id'] = usuario.id_usuario
    refresh['correo'] = usuario.correo
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'usuario': {
            'id': usuario.id_usuario,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'rol': usuario.id_rol.nombre if usuario.id_rol else None
        }
    }


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------
class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo')
        password = request.data.get('password')
        nombre = request.data.get('nombre')
        apellido = request.data.get('apellido', '')

        if not correo or not password or not nombre:
            return Response(
                {'error': 'correo, password y nombre son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Usuario.objects.filter(correo=correo).exists():
            return Response(
                {'error': 'Ya existe un usuario con ese correo.'},
                status=status.HTTP_409_CONFLICT
            )

        rol, _ = Rol.objects.get_or_create(
            nombre='usuario',
            defaults={'descripcion': 'Usuario estándar del sistema'}
        )

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usuario = Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=password_hash,
            estado='activo',
            id_rol=rol
        )

        return Response(_generar_tokens(usuario), status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Activar 2FA — genera secreto y QR (requiere autenticación)
# ---------------------------------------------------------------------------
class ActivarDosFactorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        secreto = generar_secreto()
        uri = generar_qr_uri(secreto, request.user.correo)
        qr_base64 = generar_qr_base64(uri)

        # Crea o actualiza el registro 2FA (verificado=False hasta confirmar)
        Autenticacion2FA.objects.update_or_create(
            id_usuario=request.user,
            defaults={
                'metodo': 'totp',
                'secreto': secreto,
                'verificado': False,
                'fecha_activacion': None,
            }
        )

        return Response({
            'qr_base64': qr_base64,
            'secreto_manual': secreto,
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Confirmar 2FA — verifica el primer código y activa definitivamente
# ---------------------------------------------------------------------------
class ConfirmarDosFactorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        codigo = request.data.get('codigo', '').strip()
        if not codigo:
            return Response(
                {'error': 'El campo "codigo" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            registro_2fa = Autenticacion2FA.objects.get(id_usuario=request.user)
        except Autenticacion2FA.DoesNotExist:
            return Response(
                {'error': 'No hay un proceso de activación 2FA iniciado. Llama primero a /api/2fa/activar/.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verificar_codigo(registro_2fa.secreto, codigo):
            return Response(
                {'error': 'Código incorrecto o expirado. Verifica tu app autenticadora.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Marcar como verificado
        registro_2fa.verificado = True
        registro_2fa.fecha_activacion = timezone.now()
        registro_2fa.save()

        # Actualizar flag en el modelo Usuario
        request.user.dos_factor = True
        request.user.save(update_fields=['dos_factor'])

        return Response({'mensaje': '2FA activado correctamente.'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Verificar login 2FA — recibe correo + código y emite tokens JWT
# ---------------------------------------------------------------------------
class VerificarLoginDosFactorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo', '').strip()
        codigo = request.data.get('codigo', '').strip()

        if not correo or not codigo:
            return Response(
                {'error': 'Los campos "correo" y "codigo" son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if usuario.estado != 'activo':
            return Response(
                {'error': 'Usuario inactivo o bloqueado.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            registro_2fa = Autenticacion2FA.objects.get(id_usuario=usuario, verificado=True)
        except Autenticacion2FA.DoesNotExist:
            return Response(
                {'error': '2FA no está activado para este usuario.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verificar_codigo(registro_2fa.secreto, codigo):
            return Response(
                {'error': 'Código de verificación incorrecto o expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        registrar_bitacora(
            usuario=usuario,
            codigo='001',
            descripcion=f"Inicio de sesion: {usuario.correo}",
            request=request
        )

        return Response(_generar_tokens(usuario), status=status.HTTP_200_OK)
