from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    correo = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=20, default='activo')
    dos_factor = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')

    class Meta:
        managed = False
        db_table = 'usuarios'

    def __str__(self):
        return self.correo


class Autenticacion2FA(models.Model):
    id_usuario = models.OneToOneField(Usuario, models.DO_NOTHING, db_column='id_usuario', primary_key=True)
    metodo = models.CharField(max_length=20)
    secreto = models.CharField(max_length=255, blank=True, null=True)
    verificado = models.BooleanField(default=False)
    fecha_activacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autenticacion_2fa'


class TipoTransaccion(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'tipos_transaccion'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Bitacora(models.Model):
    id_bitacora = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    codigo_transaccion = models.ForeignKey(TipoTransaccion, models.DO_NOTHING, db_column='codigo_transaccion', blank=True, null=True)
    accion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitacora'


class FuenteDatos(models.Model):
    id_fuente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    url_base = models.CharField(max_length=255)
    tipo_dato = models.CharField(max_length=50, blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'fuentes_datos'

    def __str__(self):
        return self.nombre


class Widget(models.Model):
    id_widget = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_grafico = models.CharField(max_length=20)
    id_fuente = models.ForeignKey(FuenteDatos, models.DO_NOTHING, db_column='id_fuente', blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'widgets'

    def __str__(self):
        return self.nombre


class UsuarioWidget(models.Model):
    id_usuario_widget = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    id_widget = models.ForeignKey(Widget, models.DO_NOTHING, db_column='id_widget')
    visible = models.BooleanField(default=True)
    orden = models.IntegerField(blank=True, null=True)
    configuracion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_widget'
        unique_together = (('id_usuario', 'id_widget'),)


class HistorialConsulta(models.Model):
    id_consulta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_fuente = models.ForeignKey(FuenteDatos, models.DO_NOTHING, db_column='id_fuente', blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    fecha_consulta = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'historial_consultas'


class DatoApi(models.Model):
    id_dato = models.AutoField(primary_key=True)
    id_consulta = models.ForeignKey(HistorialConsulta, models.DO_NOTHING, db_column='id_consulta')
    fuente = models.CharField(max_length=50)
    indicador = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)
    unidad = models.CharField(max_length=30, blank=True, null=True)
    fecha_dato = models.DateField(blank=True, null=True)
    payload_json = models.TextField(blank=True, null=True)
    fecha_consulta = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'datos_api'
