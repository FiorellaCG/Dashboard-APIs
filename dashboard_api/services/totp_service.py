import io
import base64
import pyotp
import qrcode


def generar_secreto() -> str:
    """Genera y retorna un secreto TOTP aleatorio en base32."""
    return pyotp.random_base32()


def generar_qr_uri(secreto: str, correo_usuario: str) -> str:
    """Retorna la URI de aprovisionamiento TOTP para el usuario."""
    return pyotp.totp.TOTP(secreto).provisioning_uri(
        name=correo_usuario,
        issuer_name='Dashboard APIs'
    )


def generar_qr_base64(uri: str) -> str:
    """
    Genera una imagen QR a partir de la URI TOTP, la codifica en base64 (PNG)
    y retorna el string listo para usar en <img src="data:image/png;base64,...">
    """
    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def verificar_codigo(secreto: str, codigo: str) -> bool:
    """
    Verifica un código TOTP de 6 dígitos contra el secreto dado.
    valid_window=1 permite un margen de ±30 segundos (un intervalo antes/después).
    """
    return pyotp.totp.TOTP(secreto).verify(codigo, valid_window=1)
