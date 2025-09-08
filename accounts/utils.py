
import threading
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from twilio.rest import Client
import random
import string

# -----------------------------
# Génération de mot de passe
# -----------------------------
def generate_password():
    """Génère un mot de passe aléatoire"""
    return get_user_model().objects.make_random_password()

# -----------------------------
# Génération d'identifiants courts
# -----------------------------
def generate_student_id():
    """Crée un matricule étudiant unique au format 25TGAXXXX"""
    user_model = get_user_model()
    year = str(timezone.now().year)[-2:]  # "25" pour 2025
    prefix = "TGA"  # Pour étudiant

    for _ in range(20):
        number = random.randint(1000, 9999)
        student_id = f"{year}{prefix}{number}"

        try:
            with transaction.atomic():
                if not user_model.objects.select_for_update().filter(
                    is_student=True,
                    username=student_id
                ).exists():
                    return student_id
        except IntegrityError:
            continue

    raise Exception("Impossible de générer un student_id unique après 20 essais")

def generate_lecturer_id():
    """Crée un matricule enseignant unique au format 25TGAXXXX"""
    user_model = get_user_model()
    year = str(timezone.now().year)[-2:]  # "25" pour 2025
    prefix = "TGA"  # Pour enseignant

    for _ in range(20):
        number = random.randint(1000, 9999)
        lecturer_id = f"{year}{prefix}{number}"

        try:
            with transaction.atomic():
                if not user_model.objects.select_for_update().filter(
                    is_lecturer=True,
                    username=lecturer_id
                ).exists():
                    return lecturer_id
        except IntegrityError:
            continue

    raise Exception("Impossible de générer un lecturer_id unique après 20 essais")

def generate_admin_id():
    """Crée un matricule admin unique au format 25ADMXXXX"""
    user_model = get_user_model()
    year = str(timezone.now().year)[-2:]  # "25" pour 2025
    prefix = "ADM"  # Pour admin

    for _ in range(20):
        number = random.randint(1000, 9999)
        admin_id = f"{year}{prefix}{number}"

        try:
            with transaction.atomic():
                if not user_model.objects.select_for_update().filter(
                    is_staff=True,
                    username=admin_id
                ).exists():
                    return admin_id
        except IntegrityError:
            continue

    raise Exception("Impossible de générer un admin_id unique après 20 essais")

# -----------------------------
# Génération credentials
# -----------------------------
def generate_student_credentials():
    return generate_student_id(), generate_password()

def generate_lecturer_credentials():
    return generate_lecturer_id(), generate_password()

def generate_admin_credentials():
    return generate_admin_id(), generate_password()

# -----------------------------
# Envoi d'emails
# -----------------------------
def send_html_email(subject, recipient_list, template, context):
    """Envoi d'un email HTML basé sur un template"""
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_FROM_ADDRESS,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

class EmailThread(threading.Thread):
    def __init__(self, subject, recipient_list, template_name, context):
        self.subject = subject
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_html_email(
                subject=self.subject,
                recipient_list=self.recipient_list,
                template=self.template_name,
                context=self.context,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

def send_new_account_email(user, password):
    """Envoi d’un email de confirmation de compte"""
    if user.is_student:
        template = "accounts/email/new_student_account_confirmation.html"
    elif user.is_lecturer:
        template = "accounts/email/new_lecturer_account_confirmation.html"
    elif user.is_staff:
        template = "accounts/email/new_admin_account_confirmation.html"
    else:
        return

    EmailThread(
        subject="Confirmation de votre compte The Genius Academy",
        recipient_list=[user.email],
        template_name=template,
        context={"user": user, "password": password}
    ).start()

# -----------------------------
# Envoi de SMS
# -----------------------------
class SMSThread(threading.Thread):
    def __init__(self, phone_number, message):
        self.phone_number = phone_number
        self.message = message
        threading.Thread.__init__(self)

    def run(self):
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                to=self.phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=self.message
            )
        except Exception as e:
            print("SMS sending failed:", e)

def send_sms(phone_number, message):
    """Envoie un SMS sans bloquer le serveur"""
    if not phone_number:
        return False
    SMSThread(phone_number, message).start()
    return True

def send_new_account_sms(user, password):
    """Envoi d’un SMS avec identifiants utilisateur"""
    phone_number = getattr(user, "phone", None)
    if not phone_number:
        return

    if user.is_student:
        role = "Etudiant"
    elif user.is_lecturer:
        role = "Enseignant"
    elif user.is_staff:
        role = "Admin"
    else:
        role = "Utilisateur"

    message = (
        f"Bonjour {user.get_full_name()}, vos identifiants The Genius Academy :\n"
        f"Rôle: {role}\n"
        f"ID: {user.username}\nMot de passe: {password}"
    )
    send_sms(phone_number, message)
