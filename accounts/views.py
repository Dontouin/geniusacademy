from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django_filters.views import FilterView
from xhtml2pdf import pisa
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied

from accounts.decorators import admin_required
from accounts.forms import (
    TeacherAddForm,  # Remplacement de StaffAddForm
    StudentAddForm,
    ParentAddForm,
    OtherAddForm,
    ProfileUpdateForm,
    TeacherInfoForm,
)
from accounts.models import User, Student, Parent, Teacher, TeacherInfo
from accounts.filters import LecturerFilter, StudentFilter, ParentFilter, OtherFilter
from django.db import transaction
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from django.conf import settings

# ----------------------------------------
# PDF utility
# ----------------------------------------
def render_to_pdf(template_name, context):
    """Rendu d'un template donné au format PDF."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="list.pdf"'
    template = render_to_string(template_name, context)
    pdf = pisa.CreatePDF(template, dest=response)
    if pdf.err:
        return HttpResponse("Erreur lors de la génération du PDF")
    return response

# ----------------------------------------
# Validation AJAX du nom d'utilisateur
# ----------------------------------------
def validate_username(request):
    username = request.GET.get("username", None)
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"is_taken": is_taken})

# ----------------------------------------
# Vues pour choisir le type d'inscription
# ----------------------------------------
def register_choice(request):
    """Page pour choisir le type d'utilisateur à enregistrer : étudiant, parent, enseignant, autre."""
    return render(request, "registration/register_choice.html")

# ---------------------------
# Vue de connexion
# ---------------------------
def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")  # Redirige si déjà connecté

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bon retour, {user.get_full_name()} !")
            next_url = request.GET.get("next")
            return redirect(next_url or "home")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "registration/login.html", {"title": "Connexion"})

# ---------------------------
# Vue de déconnexion
# ---------------------------
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")

# ########################################################
# Vues d'inscription multi-types
# ########################################################
def register_user(request, user_type):
    """
    Vue universelle pour enregistrer un utilisateur selon son type.
    user_type: 'student', 'parent', 'lecturer', 'other'
    """
    form = None
    template = None

    if user_type == "student":
        form = StudentAddForm(request.POST or None)
        template = "registration/register_student.html"
    elif user_type == "parent":
        form = ParentAddForm(request.POST or None)
        template = "registration/register_parent.html"
    elif user_type == "lecturer":
        form = TeacherAddForm(request.POST or None)  # Utilisation de TeacherAddForm
        template = "registration/register_lecturer.html"
    elif user_type == "other":
        form = OtherAddForm(request.POST or None)
        template = "registration/register_other.html"
    else:
        messages.error(request, "Type d'inscription invalide.")
        return redirect("register_choice")

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Compte {user_type.capitalize()} créé avec succès. Veuillez vous connecter.")
        return redirect("login")
    elif request.method == "POST":
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")

    return render(request, template, {"form": form, "title": f"Inscription {user_type.capitalize()}"})

# ########################################################
# Vues de profil
# ########################################################
@login_required
def profile(request):
    """Afficher le profil de l'utilisateur connecté."""
    context = {
        "title": request.user.get_full_name,
    }

    if request.user.is_lecturer:
        return render(request, "accounts/profile.html", context)
    if request.user.is_student:
        student = get_object_or_404(Student, student__pk=request.user.id)
        parent = Parent.objects.filter(student=student).first()
        context.update({
            "parent": parent,
            "level": student.level,
        })
        return render(request, "accounts/profile.html", context)

    # Pour superuser ou autre staff
    staff = User.objects.filter(is_lecturer=True)
    context["staff"] = staff
    return render(request, "accounts/profile.html", context)

@login_required
@admin_required
def profile_single(request, user_id):
    """Afficher le profil d'un utilisateur sélectionné."""
    if request.user.id == user_id:
        return redirect("profile")

    user = get_object_or_404(User, pk=user_id)
    context = {
        "title": user.get_full_name,
        "user": user,
    }

    if user.is_lecturer:
        context["user_type"] = "Enseignant"
    elif user.is_student:
        student = get_object_or_404(Student, student__pk=user_id)
        context.update({
            "user_type": "Étudiant",
            "student": student,
        })
    else:
        context["user_type"] = "Superutilisateur"

    if request.GET.get("download_pdf"):
        return render_to_pdf("pdf/profile_single.html", context)

    return render(request, "accounts/profile_single.html", context)

@login_required
@admin_required
def admin_panel(request):
    """Rendu du panneau d'administration."""
    return render(request, "setting/admin_panel.html", {"title": "Panneau d'Administration"})

# ########################################################
# Vues des paramètres
# ########################################################
@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect("profile")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "setting/profile_info_change.html", {"form": form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été mis à jour avec succès !")
            return redirect("profile")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "setting/password_change.html", {"form": form})

# ########################################################
# Vues des enseignants
# ########################################################
@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = TeacherAddForm(request.POST)  # Utilisation de TeacherAddForm
        if form.is_valid():
            lecturer = form.save()
            full_name = lecturer.get_full_name
            email = lecturer.email
            messages.success(
                request,
                f"Compte pour l'enseignant {full_name} créé. "
                f"Un email avec les identifiants sera envoyé à {email} dans une minute."
            )
            return redirect("lecturer_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = TeacherAddForm()
    return render(
        request, "accounts/add_staff.html", {"title": "Ajouter un Enseignant", "form": form}
    )

@login_required
@admin_required
def edit_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=lecturer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Enseignant {lecturer.get_full_name()} mis à jour.")
            return redirect("lecturer_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileUpdateForm(instance=lecturer)
    return render(
        request, "accounts/edit_lecturer.html", {"title": "Modifier un Enseignant", "form": form}
    )

@method_decorator([login_required, admin_required], name="dispatch")
class LecturerFilterView(FilterView):
    model = User
    filterset_class = LecturerFilter
    template_name = "accounts/lecturer_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        return User.objects.filter(is_lecturer=True)

@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, f"Enseignant {full_name} supprimé.")
    return redirect("lecturer_list")

# ########################################################
# Vues des étudiants
# ########################################################
@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            student = form.save()
            full_name = student.get_full_name
            email = student.email
            messages.success(
                request,
                f"Compte pour {full_name} créé. "
                f"Un email avec les identifiants sera envoyé à {email} dans une minute."
            )
            return redirect("student_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = StudentAddForm()
    return render(
        request, "accounts/add_student.html", {"title": "Ajouter un Étudiant", "form": form}
    )

@login_required
@admin_required
def edit_student(request, pk):
    student_user = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Étudiant {student_user.get_full_name()} mis à jour.")
            return redirect("student_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileUpdateForm(instance=student_user)
    return render(
        request, "accounts/edit_student.html", {"title": "Modifier un Étudiant", "form": form}
    )

@method_decorator([login_required, admin_required], name="dispatch")
class StudentListView(FilterView):
    model = Student
    filterset_class = StudentFilter
    template_name = "accounts/student_list.html"
    context_object_name = "filter"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Étudiants"
        return context

@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    full_name = student.student.get_full_name
    student.delete()
    messages.success(request, f"Étudiant {full_name} supprimé.")
    return redirect("student_list")

# ########################################################
# Vues des parents
# ########################################################
@method_decorator([login_required, admin_required], name="dispatch")
class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = "accounts/parent_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Parent ajouté avec succès.")
        return super().form_valid(form)

@login_required
@admin_required
def parent_list(request):
    parents = Parent.objects.select_related('parent', 'student__student').all()
    return render(request, "accounts/parent_list.html", {"parents": parents, "title": "Liste des Parents"})

# ########################################################
# Vues des autres utilisateurs
# ########################################################
@login_required
@admin_required
def other_add_view(request):
    if request.method == "POST":
        form = OtherAddForm(request.POST)
        if form.is_valid():
            other_user = form.save()
            messages.success(request, f"Utilisateur autre {other_user.get_full_name()} ajouté avec succès.")
            return redirect("other_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = OtherAddForm()
    return render(request, "accounts/add_other.html", {"title": "Ajouter un Autre Utilisateur", "form": form})

@login_required
@admin_required
def edit_other(request, pk):
    other_user = get_object_or_404(User, is_other=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=other_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur autre {other_user.get_full_name()} mis à jour.")
            return redirect("other_list")
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileUpdateForm(instance=other_user)
    return render(request, "accounts/edit_other.html", {"title": "Modifier un Autre Utilisateur", "form": form})

@login_required
@admin_required
def delete_other(request, pk):
    other_user = get_object_or_404(User, is_other=True, pk=pk)
    full_name = other_user.get_full_name()
    other_user.delete()
    messages.success(request, f"Utilisateur autre {full_name} supprimé.")
    return redirect("other_list")

@login_required
@admin_required
def other_list(request):
    others = User.objects.filter(is_other=True)
    return render(request, "accounts/other_list.html", {"others": others, "title": "Liste des Autres Utilisateurs"})

# ########################################################
# Vues des informations des enseignants
# ########################################################
@login_required
def teacher_info_add(request):
    user = request.user
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={'speciality': '', 'diploma': ''}
    )

    if request.method == "POST":
        form = TeacherInfoForm(request.POST, request.FILES)
        if form.is_valid():
            info = form.save(commit=False)
            info.teacher = teacher
            info.save()
            messages.success(request, "Fiche d'information de l'enseignant enregistrée.")
            return redirect("teacher_info_pdf", pk=info.pk)
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = TeacherInfoForm()
    
    return render(request, "accounts/teacher_info_form.html", {"title": "Informations Enseignant", "form": form})

@login_required
def teacher_info_edit(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    if request.method == "POST":
        form = TeacherInfoForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations de l'enseignant mises à jour.")
            return redirect("profile_single", user_id=info.teacher.user.id)
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = TeacherInfoForm(instance=info)
    return render(request, "accounts/teacher_info_form.html", {"title": "Modifier les Informations Enseignant", "form": form})

@login_required
def teacher_info_delete(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    teacher_name = info.teacher.user.get_full_name()
    info.delete()
    messages.success(request, f"Fiche d'information pour {teacher_name} supprimée.")
    return redirect("profile_single", user_id=info.teacher.user.id)

@login_required
def teacher_info_pdf(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_repetiteur_{info.nom}_{info.prenom}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    width, height = A4
    p = canvas.Canvas(response, pagesize=A4)

    # === Filigrane discret ===
    p.saveState()
    p.setFont("Helvetica-Bold", 60)
    p.setFillColorRGB(0.92, 0.92, 0.92)
    p.translate(width/2, height/2)
    p.rotate(45)
    p.drawCentredString(0, 0, "THE GENIUS ACADEMY")
    p.restoreState()

    # === Bandeau République / Académie ===
    def draw_header(x_center, country_fr, country_en):
        stars = "★ ★ ★ ★ ★"
        spacing = 20
        # Français
        y = height - 55
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(x_center, y, country_fr)
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center, y, stars)
        y -= spacing
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredString(x_center, y, "Paix - Travail - Patrie")
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center, y, stars)
        y -= spacing
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(x_center, y, "THE GENIUS ACADEMY")

        # Anglais
        y = height - 55
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(x_center + width/2, y, country_en)
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center + width/2, y, stars)
        y -= spacing
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredString(x_center + width/2, y, "Peace - Work - Fatherland")
        y -= spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_center + width/2, y, stars)
        y -= spacing
        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(x_center + width/2, y, "THE GENIUS ACADEMY")

    draw_header(width/4, "REPUBLIQUE DU CAMEROUN", "REPUBLIC OF CAMEROON")

    # === Logo ===
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo2.jpg")
    logo_size = 100
    logo_y_offset = 135 - (logo_size - 60)/2
    if os.path.exists(logo_path):
        p.drawImage(logo_path, width/2 - logo_size/2, height - logo_y_offset, width=logo_size, height=logo_size, mask='auto')

    # === Titre principal et référence ===
    p.setFillColor(colors.darkblue)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height - 165, "FICHE D’ENREGISTREMENT POUR RÉPÉTITEUR")
    p.setFont("Helvetica-BoldOblique", 12)
    p.drawCentredString(width/2, height - 190, "DE THE GENIUS ACADEMY")
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.black)
    p.drawCentredString(width/2, height - 210, f"NOUS CONTACTER: +237 680700470 /+237 693501411")

    # === Infos Personnelles ===
    y_top = height - 235
    y_title = y_top - 10
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.HexColor("#0D47A1"))
    p.drawString(50, y_title, "➤ INFORMATIONS PERSONNELLES :")
    p.setFillColor(colors.black)

    y = y_title - 25
    col1_x = 60
    col2_x = 200
    row_height = 18
    padding = 12
    y_box_start = y + row_height + padding

    lignes = [
        ("Nom et Prénoms", f"{info.nom} {info.prenom}"),
        ("Date de naissance", info.date_naissance.strftime('%d/%m/%Y') if info.date_naissance else ""),
        ("Lieu de naissance", info.lieu_naissance or ""),
        ("Sexe", info.sexe or ""),
        ("Nationalité", info.nationalite or ""),
        ("Statut matrimonial", info.statut_matrimonial or ""),
        ("Adresse", info.adresse or ""),
        ("Email", info.email or ""),
        ("Téléphone", info.contact or ""),
        ("N° CNI / Récépissé", info.cni_numero or ""),
        ("Personne à contacter", f"{info.personne_urgence or ''}"),
        ("Numéro d'urgence", f"{info.contact_urgence or ''}")
    ]

    for label, value in lignes:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(col1_x, y, f"{label} :")
        p.setFont("Helvetica", 10)
        p.drawString(col2_x, y, value)
        y -= row_height

    p.setStrokeColor(colors.HexColor("#0D47A1"))
    p.setLineWidth(1.5)
    p.roundRect(35, y, width - 70, y_box_start - y + 5, radius=10, stroke=1, fill=0)

    # === Matricule et Photo ===
    matricule_y = y + (y_box_start - y - 110)/2 + 110 + 10
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width - 120, matricule_y, f"Matricule : {info.matricule or 'N/A'}")

    photo_width = 90
    photo_height = 110
    photo_x = width - 160
    photo_y = y + (y_box_start - y - photo_height)/2
    p.setLineWidth(1)
    p.setStrokeColor(colors.darkblue)
    p.rect(photo_x, photo_y, photo_width, photo_height, stroke=1, fill=0)
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(photo_x + photo_width/2, photo_y - 12, "PHOTO 4x4")
    if info.photo and os.path.exists(info.photo.path):
        p.drawImage(info.photo.path, photo_x, photo_y, width=photo_width, height=photo_height, mask='auto')

    # === Infos Professionnelles ===
    y_top2 = y - 20
    y_title2 = y_top2 - 10
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.HexColor("#BF360C"))
    p.drawString(50, y_title2, "➤ INFORMATIONS PROFESSIONNELLES :")
    p.setFillColor(colors.black)

    y = y_title2 - 25
    y_box2_start = y + row_height + padding

    lignes2 = [
        ("Section d’enseignement", info.section_enseignement or ""),
        ("Domaine d’enseignement", info.domaine_enseignement or ""),
        ("Niveau scolaire", info.niveau_scolaire or ""),
        ("Diplôme le plus élevé", info.diplome or ""),
        ("Marge d’enseignement", info.marge_enseignement or ""),
        ("Matières du primaire", info.matieres_primaire or ""),
        ("Matières du secondaire", info.matieres_secondaire or ""),
        ("Expérience professionnelle", info.experience or ""),
    ]

    for label, value in lignes2:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(col1_x, y, f"{label} :")
        p.setFont("Helvetica", 10)
        p.drawString(col2_x, y, value)
        y -= row_height

    p.setStrokeColor(colors.HexColor("#BF360C"))
    p.setLineWidth(1.5)
    p.roundRect(35, y, width - 70, y_box2_start - y + 5, radius=10, stroke=1, fill=0)

    # === Signatures finales ===
    y_sign = y - 40
    date_str = datetime.now().strftime("%d/%m/%Y")

    # Signature du répétiteur
    p.setFont("Helvetica", 10)
    p.drawString(60, y_sign, "Signature du Répétiteur")

    # Signature de l’administrateur
    right_x = width - 200
    y_sign_admin = y_sign - 5
    p.drawString(right_x, y_sign_admin, f"Fait à Yaoundé, le {date_str}")
    p.drawString(right_x, y_sign_admin - 20, "Directeur Général")

    # Signature en arrière-plan
    sign_path = os.path.join(settings.BASE_DIR, "static", "img", "signature_admin.png")
    if os.path.exists(sign_path):
        sign_width = 150
        sign_height = 90
        p.drawImage(sign_path, right_x + 40, y_sign_admin - 80, width=sign_width, height=sign_height, mask='auto')

    # Cachet central
    cachet_path = os.path.join(settings.BASE_DIR, "static", "img", "cachet.png")
    cachet_width = 130
    cachet_height = 130
    if os.path.exists(cachet_path):
        p.drawImage(cachet_path, width/2 - cachet_width/2, y_sign - 90, width=cachet_width, height=cachet_height, mask='auto')

    p.showPage()
    p.save()
    return response

# ----------------------------------------
# Filtres et listes
# ----------------------------------------
@method_decorator([login_required, admin_required], name="dispatch")
class LecturerFilterView(FilterView):
    model = User
    filterset_class = LecturerFilter
    template_name = "accounts/lecturer_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        return User.objects.filter(is_lecturer=True)

@method_decorator([login_required, admin_required], name="dispatch")
class StudentFilterView(FilterView):
    model = Student
    filterset_class = StudentFilter
    template_name = "accounts/student_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        return Student.objects.all()

@method_decorator([login_required, admin_required], name="dispatch")
class OtherFilterView(FilterView):
    model = User
    filterset_class = OtherFilter
    template_name = "accounts/other_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        queryset = User.objects.filter(is_other=True)
        self.filter = OtherFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

@method_decorator([login_required, admin_required], name="dispatch")
class ParentFilterView(FilterView):
    model = Parent
    filterset_class = ParentFilter
    template_name = "accounts/parent_list.html"
    context_object_name = "filter"
    paginate_by = 20

    def get_queryset(self):
        return Parent.objects.select_related('parent', 'student__student').all()

# ----------------------------------------
# Exportation des listes en PDF
# ----------------------------------------
@login_required
@admin_required
def render_lecturer_pdf_list(request):
    lecturers = User.objects.filter(is_lecturer=True)
    context = {"lecturers": lecturers, "title": "Liste des Enseignants"}
    return render_to_pdf("pdf/lecturer_list.html", context)

@login_required
@admin_required
def render_student_pdf_list(request):
    students = Student.objects.all()
    context = {"students": students, "title": "Liste des Étudiants"}
    return render_to_pdf("pdf/student_list.html", context)

@login_required
@admin_required
def render_other_pdf_list(request):
    others = User.objects.filter(is_other=True)
    context = {"others": others, "title": "Liste des Autres Utilisateurs"}
    return render_to_pdf("pdf/other_list.html", context)

@login_required
@admin_required
def render_parent_pdf_list(request):
    parents = Parent.objects.select_related('parent', 'student__student').all()
    context = {"parents": parents, "title": "Liste des Parents"}
    return render_to_pdf("pdf/parent_list.html", context)