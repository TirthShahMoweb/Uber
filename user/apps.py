from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        # Import signals so they get registered
        import user.signals.CustomUserSignal  # If you have separate signal files

        # Or if your signals are all in one file:
        # import user.signals
