from django.core.management.base import BaseCommand
from django.conf import settings
import sqlite3
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = "Sanitize decimal fields in DB (Factura, FacturaItem) using direct sqlite3 to avoid ORM conversion errors."

    def _safe_decimal_str(self, val):
        try:
            if val is None:
                return "0.00"
            s = str(val).strip()
            if s == "" or s.lower() in {"nan", "inf", "+inf", "-inf"}:
                return "0.00"
            d = Decimal(s)
            return format(d.quantize(Decimal("0.01")), 'f')
        except (InvalidOperation, TypeError, ValueError):
            return "0.00"

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        fixed_facturas = 0
        fixed_items = 0

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Facturas
            cur.execute("SELECT id, subtotal, iva, total FROM facturas_factura")
            for row in cur.fetchall():
                rid = row["id"]
                subtotal = row["subtotal"]
                iva = row["iva"]
                total = row["total"]
                new_sub = self._safe_decimal_str(subtotal)
                new_iva = self._safe_decimal_str(iva)
                new_tot = self._safe_decimal_str(total)
                if (str(subtotal).strip() if subtotal is not None else None) != new_sub or \
                   (str(iva).strip() if iva is not None else None) != new_iva or \
                   (str(total).strip() if total is not None else None) != new_tot:
                    cur.execute(
                        "UPDATE facturas_factura SET subtotal = ?, iva = ?, total = ? WHERE id = ?",
                        (new_sub, new_iva, new_tot, rid)
                    )
                    fixed_facturas += 1

            # Items
            cur.execute("SELECT id, precio, subtotal FROM facturas_facturaitem")
            for row in cur.fetchall():
                rid = row["id"]
                precio = row["precio"]
                subtotal = row["subtotal"]
                new_precio = self._safe_decimal_str(precio)
                new_sub = self._safe_decimal_str(subtotal)
                if (str(precio).strip() if precio is not None else None) != new_precio or \
                   (str(subtotal).strip() if subtotal is not None else None) != new_sub:
                    cur.execute(
                        "UPDATE facturas_facturaitem SET precio = ?, subtotal = ? WHERE id = ?",
                        (new_precio, new_sub, rid)
                    )
                    fixed_items += 1

            conn.commit()

        self.stdout.write(self.style.SUCCESS(
            f"Sanitization complete. Facturas fixed: {fixed_facturas}, Items fixed: {fixed_items}"
        ))
