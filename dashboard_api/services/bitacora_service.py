from dashboard_api.models import Bitacora, TipoTransaccion, Usuario

def registrar_bitacora(usuario, codigo, descripcion, request=None):
    """
    Registra una transacción en la tabla Bitacora.
    :param usuario: Instancia de Usuario (o None)
    :param codigo: Código de transacción (e.g. '001', '002', '003', '004')
    :param descripcion: Descripción detallada de la acción realizada
    :param request: Objeto HttpRequest opcional para extraer la dirección IP
    """
    ip = None
    if request and hasattr(request, 'META'):
        ip = request.META.get('REMOTE_ADDR')

    user_obj = usuario if isinstance(usuario, Usuario) else None

    tipo = TipoTransaccion.objects.filter(pk=codigo).first()
    accion_nombre = tipo.nombre if tipo else f"Transacción {codigo}"

    return Bitacora.objects.create(
        id_usuario=user_obj,
        codigo_transaccion=tipo,
        accion=accion_nombre,
        descripcion=descripcion,
        ip=ip
    )
