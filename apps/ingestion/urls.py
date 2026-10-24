from django.urls import path
from .views import WhatsAppWebhookView

urlpatterns = [
    path('api/v1/integrations/whatsapp/webhook/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
    path('api/whatsapp/webhook', WhatsAppWebhookView.as_view(), name='whatsapp_webhook_direct'),
    path('api/whatsapp/webhook/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook_direct_slash'),
]
