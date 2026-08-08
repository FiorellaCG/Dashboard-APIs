from rest_framework import serializers
from .models import Widget, FuenteDatos, UsuarioWidget, HistorialConsulta, DatoApi

class FuenteDatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuenteDatos
        fields = '__all__'

class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = '__all__'

class UsuarioWidgetSerializer(serializers.ModelSerializer):
    widget_nombre = serializers.ReadOnlyField(source='id_widget.nombre')
    widget_tipo_grafico = serializers.ReadOnlyField(source='id_widget.tipo_grafico')

    class Meta:
        model = UsuarioWidget
        fields = '__all__'
        read_only_fields = ('id_usuario',)

class HistorialConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialConsulta
        fields = '__all__'

class DatoApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatoApi
        fields = '__all__'
