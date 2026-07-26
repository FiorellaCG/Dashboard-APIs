from django.apps import AppConfig


class DashboardApiConfig(AppConfig):
    name = 'dashboard_api'

    def ready(self):
        import dashboard_api.authentication
