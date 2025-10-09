from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Factura
from .serializers import FacturaSerializer
from accounts.permissions import IsEmpleadoOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
import os
try:
    import mercadopago
except Exception:
    mercadopago = None
from django.core.mail import EmailMessage
from django.conf import settings

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated, IsEmpleadoOrAdmin]

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        factura = self.get_object()
        # generate a very simple PDF using ReportLab
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 700, f"Factura: {factura.numero}")
        c.drawString(100, 680, f"Usuario: {factura.user}")
        c.drawString(100, 660, f"Total: {factura.total}")
        c.showPage()
        c.save()
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type='application/pdf')

    def _render_pdf_bytes(self, factura):
        # generate PDF bytes for reuse in email and endpoint
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 700, f"Factura: {factura.numero}")
        c.drawString(100, 680, f"Usuario: {factura.user}")
        c.drawString(100, 660, f"Total: {factura.total}")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pagar(self, request, pk=None):
        factura = self.get_object()
        # allow the factura owner (cliente) or empleado/admins to create a preference
        user = request.user
        try:
            user_role = getattr(user, 'role', None)
        except Exception:
            user_role = None
        if not (user.is_authenticated and (user == factura.user or user_role in ('admin', 'empleado'))):
            return Response({'detail': 'Permission denied.'}, status=403)
        # Create a MercadoPago preference (minimal)
        access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
        if not access_token:
            return Response({'error': 'MERCADOPAGO_ACCESS_TOKEN not configured'}, status=500)
        try:
            if mercadopago is None:
                # attempt import here for environments where it's available
                import mercadopago as _mp
                sdk = _mp.SDK(access_token)
            else:
                sdk = mercadopago.SDK(access_token)
            preference_data = {
                "items": [
                    {
                        "title": f"Factura {factura.numero}",
                        "quantity": 1,
                        "currency_id": "ARS",
                        "unit_price": float(factura.total)
                    }
                ],
                "external_reference": str(factura.id),
                "back_urls": {
                    "success": request.build_absolute_uri('/'),
                    "failure": request.build_absolute_uri('/'),
                    "pending": request.build_absolute_uri('/')
                },
            }
            preference_response = sdk.preferences().create(preference_data)
            # preference_response is a dict with 'response' key per SDK
            resp = preference_response.get('response') if isinstance(preference_response, dict) else preference_response
            preference_id = resp.get('id') if resp else None
            init_point = resp.get('init_point') if resp else None
            if preference_id:
                factura.mp_preference_id = preference_id
                factura.save()
            return Response({'preference_id': preference_id, 'init_point': init_point})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], permission_classes=[])
    def webhook(self, request):
        # Minimal webhook to process MercadoPago notifications.
        # MercadoPago can send different topic types; we'll handle payment and merchant_order
        data = request.data
        # Example payload contains 'type' and 'data' with 'id'
        topic = data.get('type') or data.get('topic')
        resource_id = None
        if 'data' in data and isinstance(data['data'], dict):
            resource_id = data['data'].get('id')
        # If external_reference provided in payment info, use it to find factura
        try:
            # Prefer to validate the payment via MercadoPago API when payment id is provided
            payment_id = data.get('payment_id') or resource_id
            factura_id = data.get('factura_id')

            # If we received only factura_id+status in payload (simple mode), use that
            status_text = data.get('status')
            if payment_id and mercadopago is not None:
                access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
                if access_token:
                    try:
                        # instantiate SDK and try common method names for payments retrieval
                        sdk = mercadopago.SDK(access_token)
                        resp = None
                        # try modern 'payments' namespace
                        try:
                            resp = sdk.payments().get(payment_id)
                        except Exception:
                            # fallback to singular 'payment'
                            try:
                                resp = sdk.payment().get(payment_id)
                            except Exception:
                                resp = None
                        # parse response
                        if isinstance(resp, dict):
                            r = resp.get('response')
                        else:
                            r = getattr(resp, 'response', None)
                        if r:
                            status_text = r.get('status')
                            ext_ref = r.get('external_reference')
                            # if the external_reference is available, use it
                            if ext_ref and not factura_id:
                                factura_id = ext_ref
                            # set payment id from response if not provided
                            payment_id = payment_id or r.get('id')
                    except Exception:
                        # if SDK fails, we fall back to provided payload values
                        pass

            if factura_id:
                f = Factura.objects.filter(id=factura_id).first()
                if not f:
                    return Response({'error': 'factura not found'}, status=404)
                if status_text in ('approved', 'paid'):
                    f.status = 'paid'
                    f.mp_payment_id = payment_id or resource_id
                    f.paid_at = timezone.now()
                    f.save()
                    # send invoice by email (non-blocking in prod would be better)
                    try:
                        self._send_invoice_email(f)
                    except Exception:
                        # Do not fail webhook if email sending fails; just log in real app
                        pass
                    return Response({'ok': True})
                elif status_text == 'cancelled':
                    f.status = 'cancelled'
                    f.save()
                    return Response({'ok': True})
            # If no factura_id, return 400 for now
            return Response({'error': 'no factura_id provided'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enviar_por_correo(self, request, pk=None):
        factura = self.get_object()
        # Only allow factura owner or empleado/admin
        user = request.user
        try:
            user_role = getattr(user, 'role', None)
        except Exception:
            user_role = None
        if not (user.is_authenticated and (user == factura.user or user_role in ('admin', 'empleado'))):
            return Response({'detail': 'Permission denied.'}, status=403)

        # Render PDF bytes and send email
        try:
            pdf_bytes = self._render_pdf_bytes(factura)
            recipient = factura.user.email
            subject = f"Factura {factura.numero} - PetMarket"
            body = f"Adjunto encontrarás la factura {factura.numero}. Total: {factura.total}"
            email = EmailMessage(subject=subject, body=body, to=[recipient])
            email.attach(f"factura_{factura.numero}.pdf", pdf_bytes, 'application/pdf')
            email.send(fail_silently=False)
            return Response({'ok': True})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def _send_invoice_email(self, factura):
        # small helper to send the invoice PDF to the factura user
        pdf_bytes = self._render_pdf_bytes(factura)
        recipient = factura.user.email
        subject = f"Factura {factura.numero} - PetMarket"
        body = f"Adjunto encontrarás la factura {factura.numero}. Total: {factura.total}"
        email = EmailMessage(subject=subject, body=body, to=[recipient])
        email.attach(f"factura_{factura.numero}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
