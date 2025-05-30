from django.apps import AppConfig


class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment'
    verbose_name = 'Pagos'

    def ready(self):
        import payment.signals  # noqa F401