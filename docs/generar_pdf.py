# -*- coding: utf-8 -*-
"""
Genera el documento PDF "Manual de Políticas - Clínica Vitalis"
que servirá como base de conocimiento para el agente de IA.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)

OUTPUT_PATH = "politicas_clinica_vitalis.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloPortada", fontSize=26, leading=32,
                           alignment=1, spaceAfter=20, textColor=colors.HexColor("#1B4F72")))
styles.add(ParagraphStyle(name="Subtitulo", fontSize=14, leading=18,
                           alignment=1, textColor=colors.HexColor("#566573")))
styles.add(ParagraphStyle(name="Seccion", fontSize=16, leading=20, spaceBefore=18,
                           spaceAfter=10, textColor=colors.HexColor("#1B4F72")))
styles.add(ParagraphStyle(name="SubSeccion", fontSize=12, leading=16, spaceBefore=10,
                           spaceAfter=6, textColor=colors.HexColor("#2874A6")))
styles.add(ParagraphStyle(name="Cuerpo", fontSize=10.5, leading=15, spaceAfter=8,
                           alignment=4))
styles.add(ParagraphStyle(name="Pregunta", fontSize=10.5, leading=15, spaceBefore=8,
                           spaceAfter=2, textColor=colors.HexColor("#1B4F72")))

story = []

# ---------- PORTADA ----------
story.append(Spacer(1, 4*cm))
story.append(Paragraph("Clínica Vitalis", styles["TituloPortada"]))
story.append(Paragraph("Manual de Políticas y Procedimientos para Pacientes", styles["Subtitulo"]))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("Versión 2.1 — Vigente desde julio de 2026", styles["Subtitulo"]))
story.append(PageBreak())

# ---------- 1. POLÍTICA DE PRIVACIDAD ----------
story.append(Paragraph("1. Política de Privacidad de Datos del Paciente", styles["Seccion"]))

story.append(Paragraph("1.1 Recolección de información", styles["SubSeccion"]))
story.append(Paragraph(
    "Clínica Vitalis recolecta datos personales y de salud de sus pacientes únicamente con fines "
    "asistenciales, administrativos y de facturación. Los datos recolectados incluyen: nombre completo, "
    "documento de identidad, fecha de nacimiento, datos de contacto, historia clínica, resultados de "
    "exámenes, y datos de convenio o cobertura médica.",
    styles["Cuerpo"]))

story.append(Paragraph("1.2 Almacenamiento y seguridad", styles["SubSeccion"]))
story.append(Paragraph(
    "Toda la información se almacena en el sistema de historia clínica electrónica (HCE) de la clínica, "
    "protegido mediante cifrado en reposo y en tránsito. El acceso está restringido al personal médico "
    "y administrativo autorizado, cada uno con credenciales individuales. Se realiza una auditoría de "
    "accesos cada 90 días.",
    styles["Cuerpo"]))

story.append(Paragraph("1.3 Retención y eliminación de datos", styles["SubSeccion"]))
story.append(Paragraph(
    "La historia clínica se conserva por un mínimo de 15 años desde la última atención, conforme a la "
    "normativa sanitaria vigente. Pasado ese plazo, el paciente puede solicitar la eliminación de sus "
    "datos administrativos, aunque la información clínica podrá anonimizarse en lugar de eliminarse "
    "por motivos de trazabilidad médica.",
    styles["Cuerpo"]))

story.append(Paragraph("1.4 Derechos del paciente", styles["SubSeccion"]))
story.append(Paragraph(
    "Todo paciente tiene derecho a acceder, rectificar y solicitar una copia de su historia clínica en "
    "un plazo máximo de 10 días hábiles desde la solicitud escrita. Las solicitudes se realizan a través "
    "del correo privacidad@clinicavitalis.com o en la recepción de la clínica.",
    styles["Cuerpo"]))

story.append(Paragraph("1.5 Terceros y convenios", styles["SubSeccion"]))
story.append(Paragraph(
    "Los datos solo se comparten con obras sociales, prepagas o aseguradoras cuando sea estrictamente "
    "necesario para autorizar prácticas o gestionar la facturación, y siempre bajo acuerdos de "
    "confidencialidad firmados con dichas entidades.",
    styles["Cuerpo"]))

story.append(PageBreak())

# ---------- 2. FAQ CONSULTAS Y TURNOS ----------
story.append(Paragraph("2. Preguntas Frecuentes sobre Consultas y Turnos", styles["Seccion"]))

faqs_turnos = [
    ("¿Cómo puedo pedir un turno?",
     "Los turnos pueden solicitarse por el sitio web de la clínica, por teléfono al (555) 234-5678, "
     "o presencialmente en recepción. La confirmación se envía por SMS o correo electrónico dentro de "
     "las 2 horas siguientes a la solicitud."),
    ("¿Con cuánta anticipación debo llegar a mi consulta?",
     "Se recomienda llegar 15 minutos antes de la hora del turno para completar el registro administrativo. "
     "Para primeras consultas o estudios con preparación previa, se recomienda llegar 30 minutos antes."),
    ("¿Qué pasa si llego tarde a mi turno?",
     "Existe una tolerancia de 10 minutos. Pasado ese tiempo, el turno podrá reprogramarse según la "
     "disponibilidad de la agenda del profesional, sin garantía de atención el mismo día."),
    ("¿Puedo pedir un turno de urgencia?",
     "Sí. Los turnos de urgencia se gestionan telefónicamente y tienen prioridad en la agenda diaria. "
     "En caso de emergencia médica grave, se recomienda dirigirse directamente a la guardia."),
    ("¿Los turnos por telemedicina están disponibles?",
     "Sí, para especialidades de seguimiento (clínica médica, nutrición, salud mental) se ofrece la "
     "modalidad de videoconsulta a través de la plataforma de la clínica."),
    ("¿Cómo sé qué documentos llevar a la consulta?",
     "Se debe presentar documento de identidad, credencial de la obra social o prepaga (si corresponde), "
     "y los estudios o informes médicos previos relacionados con el motivo de consulta."),
]

for pregunta, respuesta in faqs_turnos:
    story.append(Paragraph(pregunta, styles["Pregunta"]))
    story.append(Paragraph(respuesta, styles["Cuerpo"]))

story.append(PageBreak())

# ---------- 3. CANCELACIONES Y REAGENDAMIENTO ----------
story.append(Paragraph("3. Política de Cancelaciones y Reagendamiento", styles["Seccion"]))

story.append(Paragraph("3.1 Plazos para cancelar", styles["SubSeccion"]))
story.append(Paragraph(
    "Las cancelaciones deben realizarse con al menos 24 horas de anticipación a través del sitio web, "
    "la app de la clínica o por teléfono. Las cancelaciones con menos de 24 horas de anticipación se "
    "consideran 'tardías'.",
    styles["Cuerpo"]))

story.append(Paragraph("3.2 Inasistencias y cargos", styles["SubSeccion"]))
story.append(Paragraph(
    "La primera inasistencia sin aviso ('no-show') en un período de 12 meses no genera cargo, pero queda "
    "registrada en el historial del paciente. A partir de la segunda inasistencia sin aviso, se aplicará "
    "un cargo administrativo equivalente al 50% del valor de la consulta particular, salvo justificación "
    "médica documentada.",
    styles["Cuerpo"]))

story.append(Paragraph("3.3 Reagendamiento", styles["SubSeccion"]))
story.append(Paragraph(
    "Un turno puede reagendarse hasta dos veces sin costo adicional, siempre que se avise con al menos "
    "4 horas de anticipación. A partir del tercer reagendamiento del mismo turno original, se solicitará "
    "confirmar la asistencia mediante un pago a cuenta reembolsable.",
    styles["Cuerpo"]))

story.append(Paragraph("3.4 Cancelaciones por parte de la clínica", styles["SubSeccion"]))
story.append(Paragraph(
    "Si la clínica debe cancelar un turno (ausencia del profesional, emergencia, desperfecto técnico), "
    "se notificará al paciente lo antes posible y se ofrecerá el primer turno disponible o la modalidad "
    "de telemedicina como alternativa, sin costo adicional.",
    styles["Cuerpo"]))

story.append(PageBreak())

# ---------- 4. CONVENIOS Y COBERTURAS ----------
story.append(Paragraph("4. Guía de Convenios y Coberturas Médicas", styles["Seccion"]))

story.append(Paragraph(
    "Clínica Vitalis trabaja con las siguientes obras sociales y prepagas. El porcentaje de cobertura "
    "indicado aplica a consultas de especialidades clínicas; los estudios de diagnóstico por imágenes y "
    "prácticas de alta complejidad pueden tener coberturas distintas, sujetas a autorización previa.",
    styles["Cuerpo"]))

story.append(Spacer(1, 0.3*cm))

tabla_convenios = [
    ["Convenio", "Cobertura consulta", "Requiere autorización previa", "Copago aproximado"],
    ["SaludPlus", "100%", "No", "$0"],
    ["MedFuturo", "80%", "Solo alta complejidad", "$1.500"],
    ["Obra Social Central (OSC)", "70%", "Sí, estudios e internación", "$2.200"],
    ["PrevenSalud", "100%", "No", "$0"],
    ["Bienestar Integral", "60%", "Sí, todas las prácticas", "$2.800"],
    ["Particular (sin convenio)", "0%", "No aplica", "Valor completo de consulta"],
]

t = Table(tabla_convenios, colWidths=[4.3*cm, 3.2*cm, 5*cm, 4*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4F72")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EBF2F8")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAB7B8")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph(
    "Para las prácticas que requieren autorización previa, el paciente debe solicitar la orden médica al "
    "profesional tratante y presentarla en el área de convenios con al menos 3 días hábiles de anticipación "
    "al turno, para gestionar la autorización con la entidad correspondiente.",
    styles["Cuerpo"]))

story.append(PageBreak())

# ---------- 5. INSTRUCCIONES PRE Y POST CONSULTA ----------
story.append(Paragraph("5. Instrucciones Pre y Post Consulta", styles["Seccion"]))

story.append(Paragraph("5.1 Antes de la consulta general", styles["SubSeccion"]))
story.append(Paragraph(
    "No es necesaria una preparación especial para consultas clínicas de rutina. Se recomienda llevar "
    "un listado actualizado de medicamentos que esté tomando el paciente y los estudios previos "
    "relacionados con el motivo de consulta.",
    styles["Cuerpo"]))

story.append(Paragraph("5.2 Antes de extracciones de sangre", styles["SubSeccion"]))
story.append(Paragraph(
    "Se requiere ayuno de 8 horas para perfiles metabólicos y lipídicos, y de 12 horas si se solicita "
    "glucemia en ayunas. Se puede tomar agua durante el período de ayuno. No se debe suspender ninguna "
    "medicación sin indicación médica.",
    styles["Cuerpo"]))

story.append(Paragraph("5.3 Antes de estudios por imágenes con contraste", styles["SubSeccion"]))
story.append(Paragraph(
    "Para tomografías o resonancias con contraste se requiere ayuno de 4 horas y presentar los valores "
    "de creatinina sérica de los últimos 30 días. Pacientes con antecedentes de alergia al yodo o al "
    "contraste deben informarlo al momento de agendar el turno.",
    styles["Cuerpo"]))

story.append(Paragraph("5.4 Después de procedimientos ambulatorios menores", styles["SubSeccion"]))
story.append(Paragraph(
    "Tras procedimientos menores (biopsias, infiltraciones, pequeñas curaciones quirúrgicas) el paciente "
    "debe permanecer en observación en la clínica durante 30 minutos. Se recomienda no realizar esfuerzo "
    "físico durante las 24 horas posteriores y mantener el área tratada limpia y seca.",
    styles["Cuerpo"]))

story.append(Paragraph("5.5 Después de estudios con sedación", styles["SubSeccion"]))
story.append(Paragraph(
    "El paciente no debe conducir ni operar maquinaria durante las 12 horas posteriores a un estudio "
    "realizado con sedación. Debe retirarse acompañado de otra persona adulta responsable.",
    styles["Cuerpo"]))

story.append(Paragraph("5.6 Signos de alarma para consultar de urgencia", styles["SubSeccion"]))
story.append(Paragraph(
    "Ante fiebre mayor a 38.5°C, sangrado que no cede, dolor intenso en aumento, dificultad respiratoria "
    "o reacción alérgica luego de un procedimiento o estudio, el paciente debe dirigirse de inmediato a "
    "la guardia de la clínica o al servicio de emergencias más cercano.",
    styles["Cuerpo"]))

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter,
                         topMargin=2.5*cm, bottomMargin=2.5*cm,
                         leftMargin=2.5*cm, rightMargin=2.5*cm)
doc.build(story)
print(f"PDF generado: {OUTPUT_PATH}")
