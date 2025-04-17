# tasks/reportes.py

from .models import Venta
from django.http import HttpResponse
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime

def generar_excel_ventas():
    hoy = datetime.now()
    ventas = Venta.objects.filter(fecha__month=hoy.month, fecha__year=hoy.year)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas del Mes"
    ws.append(["Folio", "Fecha", "Usuario", "Método de Pago", "Total"])

    for v in ventas:
        ws.append([
            v.folio,
            v.fecha.strftime("%d/%m/%Y %H:%M"),
            v.usuario.username,
            v.metodo_pago,
            float(v.total)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=ventas_{hoy.strftime("%B_%Y")}.xlsx'
    wb.save(response)
    return response


def generar_pdf_ventas():
    hoy = datetime.now()
    ventas = Venta.objects.filter(fecha__month=hoy.month, fecha__year=hoy.year)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, f"Reporte de Ventas - {hoy.strftime('%B %Y').capitalize()}")
    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(40, y, "Folio       Fecha            Usuario       Método     Total")
    y -= 15

    for v in ventas:
        if y < 60:
            p.showPage()
            y = height - 40
        p.drawString(40, y, f"{v.folio}   {v.fecha.strftime('%d/%m/%Y %H:%M')}   {v.usuario.username}   {v.metodo_pago}   ${v.total:.2f}")
        y -= 15

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
