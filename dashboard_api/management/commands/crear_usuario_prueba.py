import bcrypt
from django.core.management.base import BaseCommand, CommandError
from dashboard_api.models import Usuario, Rol

class Command(BaseCommand):
    help = 'Crea un usuario de prueba para el dashboard'

    def add_arguments(self, parser):
        parser.add_argument('--correo', type=str, required=True, help='Correo del usuario')
        parser.add_argument('--password', type=str, required=True, help='Contraseña del usuario')
        parser.add_argument('--nombre', type=str, required=True, help='Nombre del usuario')
        parser.add_argument('--apellido', type=str, required=True, help='Apellido del usuario')
        parser.add_argument('--rol', type=str, default='usuario', help='Nombre del rol (default: usuario)')

    def handle(self, *args, **options):
        correo = options['correo']
        password = options['password']
        nombre = options['nombre']
        apellido = options['apellido']
        rol_nombre = options['rol']

        if Usuario.objects.filter(correo=correo).exists():
            self.stdout.write(self.style.ERROR(f'Error: El correo "{correo}" ya existe en la base de datos.'))
            return

        rol, created = Rol.objects.get_or_create(nombre=rol_nombre, defaults={'descripcion': f'Rol {rol_nombre} autogenerado'})
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Se creó el rol "{rol_nombre}".'))

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        usuario = Usuario.objects.create(
            id_rol=rol,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=password_hash,
            estado='activo'
        )

        self.stdout.write(self.style.SUCCESS(f'Éxito: Se creó el usuario con correo "{usuario.correo}" (ID: {usuario.id_usuario})'))
