"""Génération du reçu PDF (facture) remis après l'activation d'un paiement,
partagée entre l'admin (routes/admin.py) et le client final (routes/licence.py).
Mise en page inspirée du reçu Stripe/Anthropic : en-tête, bloc facturé-à,
ligne d'article, sous-total/total, historique de paiement."""
import io

from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Client, LicenceKey, Payment
from app.schemas import RecuOut

COMPANY_NAME = "Infini Software"
COMPANY_ADDRESS = ["Port-au-Prince, Haïti"]
COMPANY_EMAIL = "contact@infini-software.com"

PROVIDER_LABELS = {
    "moncash": "MonCash",
    "natcash": "NatCash",
    "stripe": "Carte bancaire",
    "manuel": "Manuel (hors-ligne)",
}

_INK = colors.HexColor("#0f172a")
_MUTED = colors.HexColor("#64748b")
_LINE = colors.HexColor("#e2e8f0")


def construire_recu(payment: Payment, db: Session) -> RecuOut:
    """Assemble les données du reçu pour un paiement déjà activé (statut
    'success') — utilisé aussi bien par l'admin (routes/admin.py) que par le
    client final via mac+clé (routes/licence.py)."""
    client = db.query(Client).filter(Client.id == payment.client_id).first()
    licence_key = (
        db.query(LicenceKey)
        .filter(LicenceKey.payment_id == payment.id)
        .order_by(LicenceKey.created_at.desc())
        .first()
    )
    return RecuOut(
        payment_id=payment.id,
        client_nom=client.nom,
        client_prenom=client.prenom,
        client_email=client.email,
        client_mac=client.mac,
        provider=payment.provider,
        amount=payment.amount,
        currency=payment.currency,
        days_valid=payment.days_valid,
        expiration_date=licence_key.expiration_date if licence_key else "",
        created_at=payment.created_at,
    )


def numero_facture(payment_id: int) -> str:
    return f"LEK-{payment_id:06d}"


def numero_recu(payment_id: int) -> str:
    """Numéro de reçu esthétique groupé par 4 chiffres, comme les reçus Stripe."""
    digits = f"{payment_id:08d}"
    return "-".join(digits[i:i + 4] for i in range(0, len(digits), 4))


_MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def _date_fr(dt) -> str:
    return f"{dt.day:02d} {_MOIS_FR[dt.month - 1]} {dt.year}"


def generer_recu_pdf(recu: RecuOut) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        title=f"Reçu {recu.payment_id}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("RecuTitle", parent=styles["Normal"], fontSize=22, fontName="Helvetica-Bold", textColor=_INK)
    brand_style = ParagraphStyle("RecuBrand", parent=styles["Normal"], fontSize=13, fontName="Helvetica-Bold", textColor=_INK, alignment=TA_RIGHT)
    label_style = ParagraphStyle("RecuLabel", parent=styles["Normal"], fontSize=9, textColor=_MUTED, leading=14)
    value_style = ParagraphStyle("RecuValue", parent=styles["Normal"], fontSize=9, textColor=_INK, leading=14)
    heading_style = ParagraphStyle("RecuHeading", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold", textColor=_INK, leading=14)
    body_style = ParagraphStyle("RecuBody", parent=styles["Normal"], fontSize=9, textColor=_INK, leading=14)
    paid_style = ParagraphStyle("RecuPaid", parent=styles["Normal"], fontSize=13, fontName="Helvetica-Bold", textColor=_INK)

    facture = numero_facture(recu.payment_id)
    recu_num = numero_recu(recu.payment_id)
    date_paiement = _date_fr(recu.created_at)
    provider_label = PROVIDER_LABELS.get(recu.provider, recu.provider.capitalize())

    elements = []

    # En-tête : titre + marque
    header = Table(
        [[Paragraph("Reçu", title_style), Paragraph("Infini<font color='#06b6d4'>Software</font>", brand_style)]],
        colWidths=[4 * inch, 3.2 * inch],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(header)
    elements.append(Spacer(1, 10))

    meta = Table(
        [
            [Paragraph("Numéro de facture", label_style), Paragraph(facture, value_style)],
            [Paragraph("Numéro de reçu", label_style), Paragraph(recu_num, value_style)],
            [Paragraph("Date de paiement", label_style), Paragraph(date_paiement, value_style)],
        ],
        colWidths=[1.6 * inch, 3 * inch],
    )
    meta.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    elements.append(meta)
    elements.append(Spacer(1, 16))

    biller = [
        Paragraph(COMPANY_NAME, heading_style),
        *[Paragraph(line, body_style) for line in COMPANY_ADDRESS],
        Paragraph(COMPANY_EMAIL, body_style),
    ]
    bill_to = [
        Paragraph("Facturé à", heading_style),
        Paragraph(f"{recu.client_prenom} {recu.client_nom}", body_style),
        Paragraph(recu.client_email, body_style),
        Paragraph(f"MAC : {recu.client_mac}", body_style),
    ]
    parties = Table([[biller, bill_to]], colWidths=[3.5 * inch, 3.5 * inch])
    parties.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(parties)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph(f"{recu.amount:g} {recu.currency} payé le {date_paiement}", paid_style))
    elements.append(Spacer(1, 14))

    items = Table(
        [
            ["Description", "Qté", "Prix unitaire", "Montant"],
            [f"Abonnement Lekol360\nExpire le {recu.expiration_date} ({recu.days_valid} jours)", "1",
             f"{recu.amount:g} {recu.currency}", f"{recu.amount:g} {recu.currency}"],
        ],
        colWidths=[3.6 * inch, 0.6 * inch, 1.4 * inch, 1.4 * inch],
    )
    items.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, 0), _MUTED),
        ("TEXTCOLOR", (0, 1), (-1, 1), _INK),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, _LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(items)

    totals = Table(
        [
            ["", "Sous-total", f"{recu.amount:g} {recu.currency}"],
            ["", "Total", f"{recu.amount:g} {recu.currency}"],
            ["", "Montant payé", f"{recu.amount:g} {recu.currency}"],
        ],
        colWidths=[4.2 * inch, 1.4 * inch, 1.4 * inch],
    )
    totals.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (1, 0), (1, -1), _MUTED),
        ("TEXTCOLOR", (2, 0), (2, -1), _INK),
        ("FONTNAME", (1, 2), (-1, 2), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (1, 0), (-1, 0), 0.75, _LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals)
    elements.append(Spacer(1, 22))

    elements.append(Paragraph("Historique de paiement", heading_style))
    elements.append(Spacer(1, 6))
    historique = Table(
        [
            ["Moyen de paiement", "Date", "Montant payé", "Numéro de reçu"],
            [provider_label, date_paiement, f"{recu.amount:g} {recu.currency}", recu_num],
        ],
        colWidths=[2 * inch, 1.8 * inch, 1.4 * inch, 1.8 * inch],
    )
    historique.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, 0), _MUTED),
        ("TEXTCOLOR", (0, 1), (-1, 1), _INK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, _LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(historique)
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=_LINE))

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_MUTED)
        canvas.drawRightString(letter[0] - 0.65 * inch, 0.45 * inch, "Page 1 sur 1")
        canvas.restoreState()

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
