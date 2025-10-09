from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Factura
import os
from unittest import mock
from django.core import mail
from django.test.utils import override_settings

User = get_user_model()

class FacturaWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='cliente_test', password='pass', email='c@test.com', role='cliente')
        self.factura = Factura.objects.create(user=self.user, numero='F-0001', total='100.00')

    @mock.patch.dict(os.environ, {'MERCADOPAGO_ACCESS_TOKEN': 'dummy'})
    @mock.patch('facturas.views.mercadopago')
    def test_pagar_creates_preference_and_saves(self, mock_mp):
        # Mock the SDK and preferences().create()
        mock_sdk = mock.MagicMock()
        mock_sdk.preferences.return_value.create.return_value = {'response': {'id': 'pref_123', 'init_point': 'https://mp/payment'}}
        mock_mp.SDK.return_value = mock_sdk

        self.client.force_authenticate(user=self.user)
        url = reverse('factura-pagar', kwargs={'pk': self.factura.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('preference_id', data)
        self.factura.refresh_from_db()
        self.assertEqual(self.factura.mp_preference_id, 'pref_123')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_enviar_por_correo_sends_email_with_pdf(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('factura-enviar-por-correo', kwargs={'pk': self.factura.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        # one message in outbox
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn(f"Factura {self.factura.numero}", message.subject)
        # ensure attachment present and is a PDF
        self.assertTrue(any(a[2] == 'application/pdf' for a in message.attachments))

    def test_webhook_marks_paid(self):
        from django.test.utils import override_settings
        url = reverse('factura-webhook')
        payload = {'factura_id': self.factura.id, 'status': 'approved', 'payment_id': 'pay_456'}
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            resp = self.client.post(url, payload, format='json')
            self.assertEqual(resp.status_code, 200)
            self.factura.refresh_from_db()
            self.assertEqual(self.factura.status, 'paid')
            self.assertEqual(self.factura.mp_payment_id, 'pay_456')
            # webhook should have sent email
            self.assertEqual(len(mail.outbox), 1)
