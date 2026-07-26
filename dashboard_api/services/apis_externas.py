import requests
import json
import os
from django.utils import timezone
from dashboard_api.models import HistorialConsulta, DatoApi, FuenteDatos


def registrar_historial_y_datos(usuario, fuente, pais, categoria, indicador, valor, unidad, fecha_dato, payload_json):
    try:
        consulta = HistorialConsulta.objects.create(
            id_usuario=usuario,
            id_fuente=fuente,
            pais=pais,
            categoria=categoria,
        )
        DatoApi.objects.create(
            id_consulta=consulta,
            fuente=fuente.nombre if fuente else 'Desconocida',
            indicador=indicador,
            pais=pais,
            valor=valor,
            unidad=unidad,
            fecha_dato=fecha_dato,
            payload_json=json.dumps(payload_json),
        )
    except Exception as e:
        print(f"Error guardando en BD: {e}")


def fetch_world_bank_data(usuario, fuente, country_code='cr', indicator='NY.GDP.MKTP.CD'):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        if len(data) > 1 and data[1]:
            for item in data[1]:
                if item.get('value') is not None:
                    valor = float(item['value'])
                    fecha = timezone.datetime(int(item['date']), 1, 1).date()
                    registrar_historial_y_datos(
                        usuario=usuario, fuente=fuente, pais=country_code, categoria='Economia',
                        indicador=indicator, valor=valor, unidad='USD', fecha_dato=fecha, payload_json=data
                    )
                    return {'valor': valor, 'pais': country_code, 'unidad': 'USD', 'fecha_dato': fecha.isoformat()}
        return {'error': 'No se encontraron datos para ese país/indicador'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error de conexión con World Bank: {e}'}
    except (KeyError, ValueError, TypeError) as e:
        return {'error': f'Respuesta inesperada de World Bank: {e}'}


def fetch_openweather_data(usuario, fuente, city='San Jose'):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return {'error': 'OPENWEATHER_API_KEY no configurada en el servidor'}

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        valor = float(data['main']['temp'])
        fecha = timezone.now().date()
        registrar_historial_y_datos(
            usuario=usuario, fuente=fuente, pais=city, categoria='Clima',
            indicador='Temperatura', valor=valor, unidad='Celsius', fecha_dato=fecha, payload_json=data
        )
        return {'valor': valor, 'pais': city, 'unidad': 'Celsius', 'fecha_dato': fecha.isoformat()}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error de conexión con OpenWeather: {e}'}
    except (KeyError, ValueError, TypeError) as e:
        return {'error': f'Ciudad no encontrada o respuesta inesperada: {e}'}


MAPEO_PAISES = {
    'costa rica': 'CR', 'mexico': 'MX', 'méxico': 'MX',
    'colombia': 'CO', 'ecuador': 'EC', 'canada': 'CA', 'canadá': 'CA',
    'estados unidos': 'US', 'usa': 'US', 'chile': 'CL', 'peru': 'PE',
    'perú': 'PE', 'argentina': 'AR', 'brasil': 'BR', 'brazil': 'BR',
    'panama': 'PA', 'panamá': 'PA', 'nicaragua': 'NI', 'honduras': 'HN',
    'guatemala': 'GT', 'el salvador': 'SV', 'republica dominicana': 'DO',
    'españa': 'ES', 'spain': 'ES', 'venezuela': 'VE', 'bolivia': 'BO',
    'paraguay': 'PY', 'uruguay': 'UY', 'cuba': 'CU',
    # Latinoamérica adicional
    'haiti': 'HT', 'haití': 'HT', 'jamaica': 'JM', 'trinidad': 'TT',
    'trinidad y tobago': 'TT', 'guyana': 'GY', 'surinam': 'SR', 'suriname': 'SR',
    'belize': 'BZ', 'belice': 'BZ',
    # Otros comunes
    'reino unido': 'GB', 'united kingdom': 'GB', 'uk': 'GB',
    'alemania': 'DE', 'germany': 'DE', 'francia': 'FR', 'france': 'FR',
    'italia': 'IT', 'italy': 'IT', 'portugal': 'PT', 'china': 'CN',
    'japon': 'JP', 'japón': 'JP', 'japan': 'JP', 'india': 'IN',
    'australia': 'AU', 'rusia': 'RU', 'russia': 'RU',
}


def fetch_restcountries_data(usuario, fuente, country_name='Costa Rica'):
    clave = country_name.strip().lower()

    if clave in MAPEO_PAISES:
        codigo = MAPEO_PAISES[clave]
    elif len(clave) == 2:
        codigo = clave.upper()
    else:
        return {'error': f'País "{country_name}" no reconocido. Intenta con el código ISO de 2 letras (ej. CR, MX, US)'}

    url = f"https://countries.dev/alpha/{codigo}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and 'population' in data:
            population = float(data.get('population', 0))
            pais_nombre = data.get('name', country_name)
            fecha = timezone.now().date()
            registrar_historial_y_datos(
                usuario=usuario, fuente=fuente, pais=pais_nombre, categoria='Geografia',
                indicador='Poblacion', valor=population, unidad='Habitantes', fecha_dato=fecha, payload_json=data
            )
            return {'valor': population, 'pais': pais_nombre, 'unidad': 'Habitantes', 'fecha_dato': fecha.isoformat()}
        return {'error': f'País "{country_name}" no encontrado'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error de conexión con REST Countries: {e}'}
    except (KeyError, ValueError, TypeError) as e:
        return {'error': f'Respuesta inesperada de REST Countries: {e}'}
