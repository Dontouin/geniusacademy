from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import User, Student, Teacher, ActivityLog
from accounts.decorators import admin_required, lecturer_required
from .forms import*
from .models import*
# En haut de votre fichier views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

# ########################################################
# News & Events
# ########################################################

from django.utils import timezone
from .models import NewsAndEvents, ActivityLog, SuccessRate

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import NewsAndEvents, ActivityLog, SuccessRate

@login_required
def home_view(request):
    items = NewsAndEvents.objects.all().order_by("-updated_date")[:5]
    activities = ActivityLog.objects.all().order_by("-created_at")[:5]

    # récupère le dernier SuccessRate enregistré
    success_obj = SuccessRate.get_latest()

    context = {
        "title": "Accueil | The Genius Academy",
        "items": items,
        "activities": activities,
        "success_rate": success_obj.rate if success_obj else 0,
        "exam_year": success_obj.year if success_obj else 'N/A',
    }
    return render(request, "core/index.html", context)

@login_required

def post_view(request):
    items = NewsAndEvents.objects.all().order_by("-updated_date")
    context = {
        "title": "News & Events",
        "items": items,
    }
    return render(request, "core/post.html", context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import User, Student, Teacher, ActivityLog
from accounts.decorators import admin_required

@login_required
@admin_required
def dashboard_view(request):
    # Logs récents
    logs = ActivityLog.objects.all().order_by("-created_at")[:10]

    # Comptage utilisateurs
    student_count = User.objects.get_student_count()
    lecturer_count = User.objects.get_lecturer_count()
    superuser_count = User.objects.filter(is_superuser=True).count()

    # Comptage hommes/femmes étudiants
    gender_counts = Student.get_gender_count()
    males_count = gender_counts.get('M', 0)
    females_count = gender_counts.get('F', 0)

    # Qualifications enseignants
    phd_count = Teacher.objects.filter(diploma__icontains='PHD').count()
    masters_count = Teacher.objects.filter(diploma__icontains='Master').count()
    bsc_count = Teacher.objects.filter(diploma__icontains='BSc').count()

    # Niveaux étudiants
    primary_count = Student.objects.filter(level='Primary').count()
    secondary_count = Student.objects.filter(level='Secondary').count()
    high_count = Student.objects.filter(level='High').count()

    context = {
        "student_count": student_count,
        "lecturer_count": lecturer_count,
        "superuser_count": superuser_count,
        "males_count": males_count,
        "females_count": females_count,
        "logs": logs,
        "teacher_qualifications": {
            'PhD': phd_count,
            'Masters': masters_count,
            'BSc': bsc_count,
        },
        "student_levels": {
            'Primary': primary_count,
            'Secondary': secondary_count,
            'High': high_count,
        },
    }

    return render(request, "core/dashboard.html", context)

@login_required
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been uploaded.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"title": "Add Post", "form": form})


@login_required
@lecturer_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been updated.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"title": "Edit Post", "form": form})


@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post_title = post.title
    post.delete()
    messages.success(request, f"{post_title} has been deleted.")
    return redirect("home")


#############################################################################################################

# core/views.py
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import DatabaseError
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
import logging

from .models import NewsletterSubscriber, GalleryImage, Testimonial, ContactMessage, Slide
from .forms import NewsletterForm, TestimonialForm, ContactForm

logger = logging.getLogger(__name__)

# =========================
# CONTEXTE GLOBAL
# =========================
def get_base_context(request, title=None):
    """Fournit le contexte commun pour toutes les vues."""
    context = {
        "title": title or _("Accueil"),
        "newsletter_form": NewsletterForm(),
        "gallery_images": [],
        "slides": [],
        "testimonials": [],
        "contact_form": ContactForm(),
        "fallback_slides": [  # Slides de secours si aucune slide en base
            {
                "images": [
                    {"image": "img/carousel1.jpg", "alt": _("Image alternative 1")},
                ],
                "title": _("L'excellence éducative à Yaoundé"),
                "description": _("Accompagnement scolaire personnalisé de la maternelle à la terminale."),
                "primary_cta": _("Nos services"),
                "primary_link": "#services",
                "secondary_cta": _("Contactez-nous"),
                "secondary_link": "#contact",
                "secondary_icon": "phone-alt",
                "tag": _("Excellence académique"),
                "tag_class": "bg-primary-600",
            },
            {
                "images": [
                    {"image": "img/carousel2.jpg", "alt": _("Image alternative 2")},
                ],
                "title": _("Une pédagogie adaptée à chaque élève"),
                "description": _("Des enseignants qualifiés pour un suivi personnalisé."),
                "primary_cta": _("Découvrir nos cours"),
                "primary_link": "#services",
                "secondary_cta": _("Nous contacter"),
                "secondary_link": "#contact",
                "secondary_icon": "envelope",
                "tag": _("Apprentissage sur mesure"),
                "tag_class": "bg-primary-500",
            },
        ],
    }

    try:
        # Images de la galerie (hors slides)
        context["gallery_images"] = GalleryImage.objects.filter(slide__isnull=True).order_by("order")[:6]

        # Slides avec leurs images (préchargement pour optimisation)
        context["slides"] = Slide.objects.prefetch_related("images").order_by("order")

        # Témoignages
        context["testimonials"] = Testimonial.objects.filter(is_active=True, is_approved=True).order_by("order")[:3]

    except DatabaseError as e:
        logger.error("Erreur lors de la récupération du contexte: %s", str(e), exc_info=True)
        messages.error(
            request,
            _("Une erreur est survenue lors du chargement des données. Veuillez réessayer plus tard."),
        )

    return context


# =========================
# VUES PRINCIPALES AMÉLIORÉES
# =========================

def about(request):
    tems = NewsAndEvents.objects.all().order_by("-updated_date")[:5]
    activities = ActivityLog.objects.all().order_by("-created_at")[:5]

    # récupère le dernier SuccessRate enregistré
    success_obj = SuccessRate.get_latest()

    context = {
        "title": "Accueil | The Genius Academy",
        "activities": activities,
        "success_rate": success_obj.rate if success_obj else 0,
        "exam_year": success_obj.year if success_obj else 'N/A',
    }
    context = get_base_context(request, _("À propos de nous"))
    
    # Récupération dynamique des statistiques
    stats = {
        'students': StatValue.objects.filter(name='students').first(),
        'teachers': StatValue.objects.filter(name='teachers').first(),
        'success_rate': StatValue.objects.filter(name='success_rate').first(),
        'years_experience': StatValue.objects.filter(name='years_experience').first(),
    }
    
    context.update(stats)
    return render(request, "core/about.html", context)

def testimonials(request):
    tems = NewsAndEvents.objects.all().order_by("-updated_date")[:5]
    activities = ActivityLog.objects.all().order_by("-created_at")[:5]

    # récupère le dernier SuccessRate enregistré
    success_obj = SuccessRate.get_latest()

    context = {
        "title": "Accueil | The Genius Academy",
        "activities": activities,
        "success_rate": success_obj.rate if success_obj else 0,
        "exam_year": success_obj.year if success_obj else 'N/A',
    }
    from .forms import TestimonialForm
    
    # Récupérer les témoignages approuvés et actifs avec pagination
    approved_testimonials = Testimonial.objects.filter(
        is_active=True, 
        is_approved=True
    ).order_by('-featured', '-created_at')
    
    # Pagination
    paginator = Paginator(approved_testimonials, 9)  # 9 témoignages par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculer la note moyenne
    from django.db.models import Avg, Count
    rating_stats = approved_testimonials.aggregate(
        average_rating=Avg('rating'),
        total_count=Count('id')
    )
    
    # Récupérer les témoignages en vedette
    featured_testimonials = approved_testimonials.filter(featured=True)[:5]
    
    context = get_base_context(request, _("Témoignages"))
    context.update({
        'testimonials': page_obj,
        'featured_testimonials': featured_testimonials,
        'average_rating': round(rating_stats['average_rating'] or 0, 1),
        'total_testimonials': rating_stats['total_count'],
        'rating_distribution': get_rating_distribution(approved_testimonials),
    })
    
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                testimonial = form.save(commit=False)
                
                # Si l'utilisateur est connecté, on lie le témoignage
                if request.user.is_authenticated:
                    testimonial.user = request.user
                    
                    # Lier automatiquement aux modèles Student ou Parent si possible
                    if hasattr(request.user, 'student'):
                        testimonial.student = request.user.student
                        testimonial.testimonial_type = Testimonial.STUDENT
                    elif hasattr(request.user, 'parent'):
                        testimonial.parent = request.user.parent
                        testimonial.testimonial_type = Testimonial.PARENT
                    elif request.user.is_lecturer:
                        testimonial.testimonial_type = Testimonial.TEACHER
                
                testimonial.is_approved = False  # Nécessite approbation admin
                testimonial.is_active = True
                testimonial.ip_address = get_client_ip(request)
                testimonial.save()
                
                # Notification à l'admin
                try:
                    send_testimonial_notification_email(testimonial)
                except Exception as e:
                    logger.warning("Erreur envoi email notification témoignage: %s", str(e))
                
                messages.success(
                    request, 
                    _("Votre témoignage a été soumis avec succès. Il sera publié après validation par notre équipe.")
                )
                return redirect("testimonials")
                
            except Exception as e:
                logger.error("Erreur soumission témoignage: %s", str(e), exc_info=True)
                messages.error(request, _("Une erreur technique est survenue lors de l'envoi de votre témoignage."))
        else:
            messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
            context["form"] = form
    else:
        # Pré-remplir si l'utilisateur est connecté
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'author': request.user.get_full_name(),
            }
            
            # Déterminer le type par défaut selon le profil
            if request.user.is_student:
                initial['testimonial_type'] = Testimonial.STUDENT
            elif request.user.is_parent:
                initial['testimonial_type'] = Testimonial.PARENT
                initial['is_parent_confirmation'] = True
            elif request.user.is_lecturer:
                initial['testimonial_type'] = Testimonial.TEACHER
        
        context["form"] = TestimonialForm(initial=initial, user=request.user)
    
    return render(request, "core/testimonials.html", context)

# Fonction utilitaire pour la distribution des notes
def get_rating_distribution(testimonials):
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for testimonial in testimonials:
        distribution[testimonial.rating] += 1
    return distribution

# Fonction utilitaire pour l'envoi d'email
def send_testimonial_notification_email(testimonial):
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = f"Nouveau témoignage soumis par {testimonial.author}"
    message = (
        f"Un nouveau témoignage a été soumis:\n\n"
        f"Auteur: {testimonial.author}\n"
        f"Type: {testimonial.get_testimonial_type_display()}\n"
        f"Note: {testimonial.rating}/5\n"
        f"Message: {testimonial.content[:200]}...\n\n"
        f"Connectez-vous à l'admin pour le modérer."
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CONTACT_EMAIL],
        fail_silently=True,
    )

# Ajouter cette vue pour gérer les requêtes AJAX de détails de témoignage
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def testimonial_detail(request, pk):
    try:
        testimonial = Testimonial.objects.get(pk=pk, is_active=True, is_approved=True)
        
        data = {
            'author': testimonial.author,
            'author_initials': testimonial.author_initials,
            'type_display': testimonial.get_type_display(),
            'rating': testimonial.rating,
            'excerpt': testimonial.excerpt,
            'full_content': testimonial.content,
            'date': testimonial.created_at.strftime("%d %B %Y"),
            'image': testimonial.image.url if testimonial.image else None,
        }
        
        return JsonResponse(data)
    except Testimonial.DoesNotExist:
        return JsonResponse({'error': 'Témoignage non trouvé'}, status=404)


def services(request):
    context = get_base_context(request, _("Nos services"))
    return render(request, "core/services.html", context)


# =========================
# PAGES STATIQUES FACTORISÉES
# =========================
def static_page_view(request, template, title):
    context = get_base_context(request, title)
    return render(request, f"core/{template}.html", context)


def faq(request):
    return static_page_view(request, "faq", _("Foire aux questions"))


def privacy(request):
    return static_page_view(request, "privacy", _("Politique de confidentialité"))


def terms(request):
    return static_page_view(request, "terms", _("Conditions d'utilisation"))


def cookies(request):
    return static_page_view(request, "cookies", _("Gestion des cookies"))


def help(request):
    return static_page_view(request, "help", _("Aide"))


# =========================
# CONTACT
# =========================
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
from django.http import HttpResponse
import logging
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, NewsletterForm  # Assure-toi que NewsletterForm est importé

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def contact(request):
    context = {}

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Récupération et nettoyage des données
                contact_message = form.save(commit=False)
                contact_message.nom = contact_message.nom.strip()
                contact_message.email = contact_message.email.strip().lower()
                contact_message.phone = contact_message.phone.strip() if contact_message.phone else ""
                contact_message.sujet = contact_message.sujet.strip()
                contact_message.message = contact_message.message.strip()
                
                # Ajout d'informations supplémentaires
                contact_message.ip_address = get_client_ip(request)
                contact_message.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
                
                contact_message.save()

                # Gestion de la newsletter
                if form.cleaned_data.get('newsletter'):
                    subscriber, created = NewsletterSubscriber.objects.get_or_create(
                        email=contact_message.email,
                        defaults={
                            "nom": contact_message.nom,
                            "is_active": True,
                            "source": "formulaire_contact"
                        },
                    )
                    if not created and not subscriber.is_active:
                        subscriber.is_active = True
                        subscriber.nom = contact_message.nom  # Mise à jour du nom
                        subscriber.save()
                        messages.info(request, _("Votre inscription à la newsletter a été réactivée."))
                    elif created:
                        messages.info(request, _("Vous êtes maintenant inscrit à notre newsletter."))

                # Envoi email à l'administrateur
                full_message = (
                    f"Nouveau message de contact reçu:\n\n"
                    f"Nom: {contact_message.nom}\n"
                    f"Email: {contact_message.email}\n"
                    f"Téléphone: {contact_message.phone or 'Non renseigné'}\n"
                    f"Niveau scolaire: {contact_message.level or 'Non spécifié'}\n"
                    f"Sujet: {contact_message.sujet}\n"
                    f"Date: {contact_message.created_at.strftime('%d/%m/%Y à %H:%M')}\n"
                    f"IP: {contact_message.ip_address}\n\n"
                    f"Message:\n{contact_message.message}\n\n"
                    f"--\nCet email a été envoyé depuis le formulaire de contact de The Genius Academy"
                )

                # Email de confirmation à l'utilisateur
                user_message = (
                    f"Bonjour {contact_message.nom},\n\n"
                    f"Nous avons bien reçu votre message et vous en remercions.\n\n"
                    f"Récapitulatif de votre message:\n"
                    f"Sujet: {contact_message.sujet}\n"
                    f"Message: {contact_message.message[:200]}...\n\n"
                    f"Nous traitons votre demande dans les plus brefs délais et vous répondrons très rapidement.\n\n"
                    f"Cordialement,\n"
                    f"L'équipe The Genius Academy\n"
                    f"Tél: +237 680700470\n"
                    f"Email: ayangluc096@gmail.com"
                )

                # Envoi des emails
                try:
                    # Email à l'admin
                    send_mail(
                        subject=f"[Contact] {contact_message.sujet} - {contact_message.nom}",
                        message=full_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.CONTACT_EMAIL, "ayangluc096@gmail.com"],
                        fail_silently=False,
                    )

                    # Email de confirmation à l'utilisateur
                    send_mail(
                        subject="The Genius Academy - Confirmation de réception de votre message",
                        message=user_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contact_message.email],
                        fail_silently=False,
                    )
                except BadHeaderError:
                    messages.error(request, _("Erreur d'en-tête dans l'envoi d'email."))
                except Exception as e:
                    logger.error("Erreur lors de l'envoi des emails: %s", e, exc_info=True)

                messages.success(request, _("Votre message a été envoyé avec succès ! Vous recevrez une confirmation par email."))
                return redirect("contact")

            except Exception as e:
                logger.error("Erreur lors de l'envoi du message de contact : %s", e, exc_info=True)
                messages.error(request, _("Une erreur technique est survenue. Veuillez réessayer ou nous contacter directement par téléphone."))

        else:
            # Ajouter les erreurs de formulaire aux messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
            context['contact_form'] = form

    else:
        # Pré-remplir le formulaire si l'utilisateur est connecté
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'nom': request.user.get_full_name(),
                'email': request.user.email,
                'phone': getattr(request.user, 'phone', ''),
            }
        context['contact_form'] = ContactForm(initial=initial_data)

    return render(request, "core/contact.html", context)


# =========================
# NEWSLETTER
# =========================
def newsletter_subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data["email"].strip().lower()
                nom = form.cleaned_data.get("nom", "").strip()

                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={
                        "nom": nom,
                        "is_active": True,
                        "source": "newsletter_form"
                    }
                )

                if not created:
                    if not subscriber.is_active:
                        subscriber.is_active = True
                        subscriber.nom = nom
                        subscriber.save()
                        messages.success(request, _("Votre inscription à la newsletter a été réactivée."))
                    else:
                        messages.info(request, _("Vous êtes déjà inscrit à notre newsletter."))
                else:
                    messages.success(request, _("Inscription à la newsletter réussie !"))

                # Email de confirmation
                try:
                    send_mail(
                        subject="Confirmation d'inscription à la newsletter - The Genius Academy",
                        message=(
                            f"Bonjour {nom or 'cher client'},\n\n"
                            "Vous êtes maintenant inscrit à la newsletter de The Genius Academy.\n"
                            "Vous recevrez nos actualités, conseils éducatifs et offres spéciales.\n\n"
                            "Pour vous désinscrire, cliquez sur le lien en bas de nos emails.\n\n"
                            "Cordialement,\n"
                            "L'équipe The Genius Academy"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error("Erreur envoi email newsletter: %s", e)

                return redirect("home")

            except Exception as e:
                logger.error("Erreur newsletter: %s", str(e), exc_info=True)
                messages.error(request, _("Une erreur est survenue. Veuillez réessayer."))
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect("home")
    else:
        return redirect("home")


# =========================
# TÉMOIGNAGES
# =========================
def submit_testimonial(request):
    from .forms import TestimonialForm
    
    context = get_base_context(request, _("Soumettre un témoignage"))
    
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                testimonial = form.save(commit=False)
                
                # Si l'utilisateur est connecté, on lie le témoignage
                if request.user.is_authenticated:
                    testimonial.user = request.user
                    testimonial.nom = request.user.get_full_name()
                    testimonial.email = request.user.email
                
                testimonial.is_approved = False
                testimonial.is_active = True
                testimonial.ip_address = get_client_ip(request)
                testimonial.save()
                
                # Notification à l'admin
                try:
                    send_mail(
                        subject=f"Nouveau témoignage soumis par {testimonial.nom}",
                        message=(
                            f"Un nouveau témoignage a été soumis:\n\n"
                            f"Nom: {testimonial.nom}\n"
                            f"Email: {testimonial.email}\n"
                            f"Note: {testimonial.note}/5\n"
                            f"Message: {testimonial.message[:200]}...\n\n"
                            f"Connectez-vous à l'admin pour le modérer."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.CONTACT_EMAIL],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                
                messages.success(
                    request, 
                    _("Votre témoignage a été soumis avec succès. Il sera publié après validation par notre équipe.")
                )
                return redirect("core:home")
                
            except Exception as e:
                logger.error("Erreur soumission témoignage: %s", str(e), exc_info=True)
                messages.error(request, _("Une erreur technique est survenue lors de l'envoi de votre témoignage."))
        else:
            messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
            context["form"] = form
    else:
        # Pré-remplir si l'utilisateur est connecté
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'nom': request.user.get_full_name(),
                'email': request.user.email,
            }
        context["form"] = TestimonialForm(initial=initial)
    
    return render(request, "core/submit_testimonial.html", context)


# Vérifie que l'utilisateur est admin
def admin_required(view_func):
    from django.contrib.auth.decorators import user_passes_test
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

# core/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from datetime import datetime
import os
from django.conf import settings
from .models import AcademicEvent
from .forms import AcademicEventForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
# from docx import Document
# from docx.shared import Inches, Pt
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
# from django import forms

# -------------------------------
# Formulaire pour générer le calendrier
# -------------------------------
class GenerateCalendarForm(forms.Form):
    start_year = forms.IntegerField(label="Année de début", min_value=2000, max_value=2100)
    end_year = forms.IntegerField(label="Année de fin", min_value=2000, max_value=2100)


# -------------------------------
# Vérification admin
# -------------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser


# -------------------------------
# Vues CRUD événements
# -------------------------------
@login_required
def event_add(request):
    if request.method == "POST":
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, "Événement ajouté avec succès ✅")
            return redirect("events_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous ❌")
    else:
        form = AcademicEventForm()
    return render(request, "core/event_form.html", {"title": "Ajouter un événement", "form": form})

@login_required
def event_edit(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == "POST":
        form = AcademicEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Événement modifié avec succès ✅")
            return redirect("events_list")
        messages.error(request, "Veuillez corriger les erreurs ❌")
    else:
        form = AcademicEventForm(instance=event)
    return render(request, "core/event_form.html", {"title": "Modifier un événement", "form": form})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    event_name = event.activity
    event.delete()
    messages.success(request, f"L’événement « {event_name} » a été supprimé ✅")
    return redirect("events_list")

@login_required
def events_list(request):
    events = AcademicEvent.objects.all()
    return render(request, "core/events_list.html", {"events": events})


# -------------------------------
# core/views.py - Génération Calendrier
# -------------------------------
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas

# from docx import Document
# from docx.shared import Pt, Inches
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from datetime import datetime
import os

from .forms import AcademicEventForm
from .models import AcademicEvent

# -------------------------------
# Vérification admin
# -------------------------------
def is_admin(user):
    return user.is_superuser or user.is_staff

# -------------------------------
# Vue principale: Ajouter événements
# -------------------------------
@login_required
@user_passes_test(is_admin)
def generate_calendar(request):
    if request.method == "POST":
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Événement ajouté avec succès ✅")
            return redirect("generate_calendar")
        else:
            messages.error(request, "Veuillez corriger les erreurs ❌")
    else:
        form = AcademicEventForm()

    events = AcademicEvent.objects.all().order_by("date")
    return render(request, "core/generate_calendar.html", {"form": form, "events": events})

# -------------------------------
# PDF Helper: Header amélioré
# -------------------------------
def header_footer(p, width, height):
    """Header PDF avec étoiles, logo et titre"""
    stars = "★ ★ ★ ★ ★"
    spacing = 18

    # République / Académie
    for x_center, lang in [(width/4, "FR"), (3*width/4, "EN")]:
        y = height - 50
        p.setFont("Helvetica-Bold", 11)
        text = "REPUBLIQUE DU CAMEROUN" if lang=="FR" else "REPUBLIC OF CAMEROON"
        p.drawCentredString(x_center, y, text)
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center, y, stars)
        y -= spacing
        p.setFont("Helvetica-Oblique", 10)
        text = "Paix – Travail – Patrie" if lang=="FR" else "Peace – Work – Fatherland"
        p.drawCentredString(x_center, y, text)
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center, y, stars)

    # Logo centré
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo2.jpg")
    if os.path.exists(logo_path):
        p.drawImage(logo_path, width/2 - 50, height - 150, width=100, height=80, mask="auto")

    # Titre
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor("#0D47A1"))
    p.drawCentredString(width/2, height - 180, "CALENDRIER DE L’ANNÉE SCOLAIRE ACADÉMIQUE")
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width/2, height - 200, f"{datetime.today().year} – {datetime.today().year+1}")
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height - 220, "DU GROUPE THE GENIUS ACADEMY")
    p.setFillColor(colors.black)

# -------------------------------
# PDF Helper: Footer
# -------------------------------
def footer_signature(p, width):
    """Footer PDF avec signatures et cachet"""
    y_footer = 70
    date_str = datetime.now().strftime("%d/%m/%Y")
    p.setFont("Helvetica", 10)
    p.drawString(50, y_footer, "Visa du Responsable Académique")
    p.drawString(width - 200, y_footer, f"Yaoundé, le {date_str}")
    p.drawString(width - 200, y_footer - 15, "Directeur Général")

    sign_path = os.path.join(settings.BASE_DIR, "static", "img", "signature_admin.png")
    if os.path.exists(sign_path):
        p.drawImage(sign_path, width - 180, y_footer - 80, width=120, height=60, mask="auto")

    cachet_path = os.path.join(settings.BASE_DIR, "static", "img", "cachet.png")
    if os.path.exists(cachet_path):
        p.drawImage(cachet_path, width/2 - 50, y_footer - 60, width=100, height=100, mask="auto")

# -------------------------------
# Générer PDF calendrier
# -------------------------------
@login_required
@user_passes_test(is_admin)
def calendrier_academique_pdf(request):
    start_year = request.session.get('calendar_start_year', datetime.now().year)
    end_year = request.session.get('calendar_end_year', start_year + 1)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="calendrier_academique.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Watermark
    p.saveState()
    p.setFont("Helvetica-Bold", 60)
    p.setFillColorRGB(0.92, 0.92, 0.92)
    p.translate(width/2, height/2)
    p.rotate(45)
    p.drawCentredString(0, 0, "THE GENIUS ACADEMY")
    p.restoreState()

    events = AcademicEvent.objects.filter(date__year__gte=start_year, date__year__lte=end_year).order_by("date")

    header_footer(p, width, height)

    # Tableau
    data = [["Dates", "Activités", "Responsable"]]
    for e in events:
        data.append([e.date.strftime("%d %b %Y"), e.activity, e.responsible])

    table = Table(data, colWidths=[100, 280, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D47A1")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 40, height - 300)

    footer_signature(p, width)
    p.showPage()
    p.save()
    return response

# -------------------------------
# Générer DOCX calendrier
# -------------------------------
@login_required
@user_passes_test(is_admin)
def calendrier_academique_docx(request):
    start_year = request.session.get('calendar_start_year', datetime.now().year)
    end_year = request.session.get('calendar_end_year', start_year + 1)

    document = Document()

    # Header République / Académie avec étoiles
    stars = "★ ★ ★ ★ ★"
    table_header = document.add_table(rows=2, cols=2)
    table_header.autofit = True
    table_header.cell(0,0).text = f"REPUBLIQUE DU CAMEROUN\n{stars}\nPaix – Travail – Patrie\n{stars}"
    table_header.cell(0,1).text = f"REPUBLIC OF CAMEROON\n{stars}\nPeace – Work – Fatherland\n{stars}"
    for cell in table_header.rows[0].cells:
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = paragraph.runs[0]
            run.font.size = Pt(10)
            run.font.bold = True

    # Logo centré
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo2.jpg")
    if os.path.exists(logo_path):
        document.add_picture(logo_path, width=Inches(1.5))
        document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Titre
    title = document.add_paragraph()
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = title.add_run("CALENDRIER DE L’ANNÉE SCOLAIRE ACADÉMIQUE\n")
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.name = "Arial"

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = subtitle.add_run(f"{start_year} – {end_year}\n")
    run.font.size = Pt(12)
    run.font.bold = True

    school = document.add_paragraph()
    school.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = school.add_run("DU GROUPE THE GENIUS ACADEMY\n\n")
    run.font.size = Pt(12)
    run.font.bold = True

    # Tableau des événements
    events = AcademicEvent.objects.filter(date__year__gte=start_year, date__year__lte=end_year).order_by("date")
    table = document.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Dates"
    hdr_cells[1].text = "Activités"
    hdr_cells[2].text = "Responsable"
    for e in events:
        row_cells = table.add_row().cells
        row_cells[0].text = e.date.strftime("%d/%m/%Y")
        row_cells[1].text = e.activity
        row_cells[2].text = e.responsible

    # Footer
    document.add_paragraph("\n\n")
    footer = document.add_table(rows=1, cols=2)
    footer.autofit = True
    footer.cell(0, 0).text = "Visa du Responsable Académique"
    footer.cell(0, 1).text = f"Yaoundé, le {datetime.now().strftime('%d/%m/%Y')}\nDirecteur Général"

    # Signatures et cachet
    sign_path = os.path.join(settings.BASE_DIR, "static", "img", "signature_admin.png")
    if os.path.exists(sign_path):
        document.add_picture(sign_path, width=Inches(2))
    cachet_path = os.path.join(settings.BASE_DIR, "static", "img", "cachet.png")
    if os.path.exists(cachet_path):
        document.add_picture(cachet_path, width=Inches(1.5))

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    response['Content-Disposition'] = 'attachment; filename="calendrier_academique.docx"'
    document.save(response)
    return response

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas

from datetime import datetime
import os

from .forms import AcademicEventForm, AbsenceForm, ReservationForm
from .models import AcademicEvent, Absence, Reservation

# -------------------------------
# Vérification secrétaire/admin
# -------------------------------
def is_secretary(user):
    return user.is_staff or user.is_superuser

# -------------------------------
# Vue principale: Ajouter événements, absences et réservations
# -------------------------------
@login_required
@user_passes_test(is_secretary)
def secretary_dashboard(request):
    saved_objects = {"events": [], "absences": [], "reservations": []}  # <-- nouveaux

    if request.method == "POST":
        event_form = AcademicEventForm(request.POST, prefix='event')
        absence_form = AbsenceForm(request.POST, prefix='absence')
        reservation_form = ReservationForm(request.POST, prefix='reservation')

        forms = [event_form, absence_form, reservation_form]
        all_valid = all(form.is_valid() for form in forms)

        if all_valid:
            saved_objects["events"].append(event_form.save())
            saved_objects["absences"].append(absence_form.save())
            saved_objects["reservations"].append(reservation_form.save())
            messages.success(request, "Données enregistrées avec succès ✅")
            # Stocker temporairement dans session pour le PDF
            request.session['secretary_report_ids'] = {
                "events": [e.id for e in saved_objects["events"]],
                "absences": [a.id for a in saved_objects["absences"]],
                "reservations": [r.id for r in saved_objects["reservations"]],
            }
            return redirect("secretary_dashboard")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans les formulaires ❌")
    else:
        event_form = AcademicEventForm(prefix='event')
        absence_form = AbsenceForm(prefix='absence')
        reservation_form = ReservationForm(prefix='reservation')

    events = AcademicEvent.objects.all().order_by("date")
    absences = Absence.objects.all().order_by("date")
    reservations = Reservation.objects.all().order_by("date")

    context = {
        "event_form": event_form,
        "absence_form": absence_form,
        "reservation_form": reservation_form,
        "events": events,
        "absences": absences,
        "reservations": reservations,
    }
    return render(request, "core/secretary_dashboard.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from datetime import datetime
import os

from .forms import AcademicEventForm, AbsenceForm, ReservationForm
from .models import AcademicEvent, Absence, Reservation


# Vérification secrétaire/admin
def is_secretary(user):
    return user.is_staff or user.is_superuser


# Tableau utilitaire
def build_table(title, columns, rows):
    styles = getSampleStyleSheet()
    elements = []

    # Titre de section
    elements.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
    elements.append(Spacer(1, 6))

    if not rows:
        elements.append(Paragraph(_("<i>No data available</i>"), styles["Normal"]))
        elements.append(Spacer(1, 12))
        return elements

    data = [columns] + rows
    table = Table(data, colWidths=[120, 200, 120])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D47A1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 18))
    return elements


@login_required
@user_passes_test(is_secretary)
def secretary_report_pdf(request):
    # Réponse HTTP
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="rapport_secretaire.pdf"'

    # Document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=40, bottomMargin=30
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Centered", alignment=TA_CENTER, fontSize=12, spaceAfter=12))
    styles.add(ParagraphStyle(name="Small", alignment=TA_LEFT, fontSize=9, textColor=colors.grey))

    elements = []

    # En-tête officiel
    elements.append(Paragraph("<b>REPUBLIQUE DU CAMEROUN</b>", styles["Centered"]))
    elements.append(Paragraph(_("Peace – Work – Fatherland"), styles["Centered"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>REPUBLIC OF CAMEROON</b>", styles["Centered"]))
    elements.append(Paragraph(_("Paix – Travail – Patrie"), styles["Centered"]))
    elements.append(Spacer(1, 12))

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo2.jpg")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=80, height=60))
        elements.append(Spacer(1, 12))

    # Titre rapport
    elements.append(Paragraph("<b><font size=14 color='#0D47A1'>"
                              f"{_('SECRETARY MANAGEMENT REPORT')}"
                              "</font></b>", styles["Centered"]))
    elements.append(Spacer(1, 24))

    # Récupération des données
    report_ids = request.session.get("secretary_report_ids", {})
    events = AcademicEvent.objects.filter(id__in=report_ids.get("events", []))
    absences = Absence.objects.filter(id__in=report_ids.get("absences", []))
    reservations = Reservation.objects.filter(id__in=report_ids.get("reservations", []))

    # Tables
    rows = [[e.date.strftime("%d/%m/%Y"), e.activity, e.responsible] for e in events]
    elements += build_table(_("Academic Events"), [_("Date"), _("Activity"), _("Responsible")], rows)

    rows = [[a.teacher.get_full_name(), a.date.strftime("%d/%m/%Y"), a.reason or ""] for a in absences]
    elements += build_table(_("Teacher Absences"), [_("Teacher"), _("Date"), _("Reason")], rows)

    rows = [[r.course_name, r.student_name, r.date.strftime("%d/%m/%Y")] for r in reservations]
    elements += build_table(_("Course Reservations"), [_("Course"), _("Student"), _("Date")], rows)

    # Signature et footer
    date_str = datetime.now().strftime("%d/%m/%Y")
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(_("Secretary's approval"), styles["Normal"]))
    elements.append(Paragraph(f"Yaoundé, le {date_str}", styles["Normal"]))

    # Signature + cachet
    sign_path = os.path.join(settings.BASE_DIR, "static", "img", "signature_admin.png")
    if os.path.exists(sign_path):
        elements.append(Image(sign_path, width=120, height=60))
    cachet_path = os.path.join(settings.BASE_DIR, "static", "img", "cachet.png")
    if os.path.exists(cachet_path):
        elements.append(Image(cachet_path, width=100, height=100))

    # Construction du document
    doc.build(elements)
    return response
