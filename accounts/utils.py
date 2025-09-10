import threading
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string

# -----------------------------
# Génération de mot de passe
# -----------------------------
def generate_password():
    """Génère un mot de passe aléatoire"""
    return get_user_model().objects.make_random_password()

# -----------------------------
# Génération d'identifiants UNIQUEMENT pour enseignants
# -----------------------------
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

# -----------------------------
# Génération credentials UNIQUEMENT pour enseignants
# -----------------------------
def generate_lecturer_credentials():
    return generate_lecturer_id(), generate_password()

# -----------------------------
# Envoi d'emails UNIQUEMENT pour enseignants
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
    """Envoi d'un email de confirmation de compte UNIQUEMENT pour les enseignants"""
    if user.is_lecturer:  # SEULEMENT pour les enseignants
        template = "accounts/email/new_lecturer_account_confirmation.html"
        
        EmailThread(
            subject="Confirmation de votre compte The Genius Academy",
            recipient_list=[user.email],
            template_name=template,
            context={"user": user, "password": password}
        ).start()
    
    # Pour tous les autres types (étudiants, parents, autres, admins)
    # NE RIEN FAIRE - pas d'envoi d'email automatique