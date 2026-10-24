import json
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DataSource, ConnectorConfig
from .connectors.whatsapp import WhatsAppCloudApiConnector
from .connectors.file_import import FileImportConnector

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    Official Webhook Endpoint for Meta WhatsApp Business Cloud API.
    GET: Verification handshake
    POST: Ingestion of incoming citizen messages with HMAC-SHA256 signature security.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        # Retrieve expected verify token from connector config or env
        connector = WhatsAppCloudApiConnector()
        expected_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "rmc_secure_verify_token_2026")

        verified, challenge_val = connector.verify_webhook_token(mode, token, challenge, expected_token)
        if verified:
            return HttpResponse(challenge_val, status=200, content_type="text/plain")
        return HttpResponse("Verification failed", status=403)

    def post(self, request):
        app_secret = os.environ.get("WHATSAPP_APP_SECRET", "rmc_demo_secret")
        signature = request.headers.get("X-Hub-Signature-256", "")

        connector = WhatsAppCloudApiConnector()

        # If production secret is configured, enforce strict HMAC verification
        if app_secret and app_secret != "rmc_demo_secret" and not connector.verify_signature(request.body, signature, app_secret):
            return Response({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return Response({"error": "Malformed JSON payload"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create WhatsApp data source
        data_source = DataSource.objects.filter(source_type="WHATSAPP").first()
        if not data_source:
            data_source = DataSource.objects.create(
                name="WhatsApp Business Cloud API",
                source_type="WHATSAPP",
                health_status="HEALTHY"
            )

        items = connector.handle_incoming_webhook(payload, data_source)
        return Response({
            "status": "success",
            "ingested_count": len(items)
        }, status=status.HTTP_200_OK)
