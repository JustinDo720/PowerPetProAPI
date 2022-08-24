from django.apps import AppConfig


class PowerPetProAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'power_pet_pro_app'

    def ready(self):
        import power_pet_pro_app.signals