from django.contrib import admin
from .models import Rol, Widget, FuenteDatos, Usuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('id_widget', 'nombre', 'tipo_grafico', 'id_fuente', 'activo')
    list_filter = ('tipo_grafico', 'activo', 'id_fuente')
    search_fields = ('nombre', 'descripcion')

@admin.register(FuenteDatos)
class FuenteDatosAdmin(admin.ModelAdmin):
    list_display = ('id_fuente', 'nombre', 'url_base', 'tipo_dato', 'activa')
    list_filter = ('activa', 'tipo_dato')
    search_fields = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'correo', 'nombre', 'apellido', 'estado', 'id_rol')
    list_filter = ('estado', 'dos_factor', 'id_rol')
    search_fields = ('correo', 'nombre', 'apellido')
