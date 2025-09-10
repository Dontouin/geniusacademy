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
    StaffAddForm,
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
    """Render a given template to PDF format."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="list.pdf"'
    template = render_to_string(template_name, context)
    pdf = pisa.CreatePDF(template, dest=response)
    if pdf.err:
        return HttpResponse("We had some problems generating the PDF")
    return response

# ----------------------------------------
# AJAX username validation
# ----------------------------------------
def validate_username(request):
    username = request.GET.get("username", None)
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"is_taken": is_taken})

# ----------------------------------------
# Multi-type registration views
# ----------------------------------------
def register_choice(request):
    """Page to choose type of user to register: student, parent, lecturer, other"""
    return render(request, "registration/register_choice.html")

# ---------------------------
# Login view
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
            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            
            # Redirection après login
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html", {"title": "Login"})

# ---------------------------
# Logout view
# ---------------------------
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# ########################################################
# Autonomous Registration Views
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
        form = StaffAddForm(request.POST or None)  # Correction: Utiliser StaffAddForm pour les enseignants
        template = "registration/register_lecturer.html"
    elif user_type == "other":
        form = OtherAddForm(request.POST or None)
        template = "registration/register_other.html"
    else:
        messages.error(request, "Invalid registration type.")
        return redirect("register_choice")

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{user_type.capitalize()} account created successfully. Please login.")
        return redirect("login")
    elif request.method == "POST":
        messages.error(request, "Please correct the errors below.")

    return render(request, template, {"form": form, "title": f"Register {user_type.capitalize()}"})

@login_required
@admin_required
def admin_panel(request):
    """Render admin dashboard panel."""
    return render(request, "setting/admin_panel.html", {"title": "Admin Panel"})

# ----------------------------------------
# Profile views
# ----------------------------------------
@login_required
def profile(request):
    """Display current user's profile with relevant info"""
    context = {
        "title": request.user.get_full_name(),
    }

    if request.user.is_student:
        student = get_object_or_404(Student, student__pk=request.user.id)
        parent = Parent.objects.filter(student=student).first()
        
        context.update({
            "student": student,
            "parent": parent,
            "level": student.level,
        })

    elif request.user.is_parent:
        parent = get_object_or_404(Parent, parent=request.user)
        children = Student.objects.filter(parent=parent)
        context.update({
            "parent": parent,
            "children": children,
        })

    elif request.user.is_other:
        context.update({
            "user_type": "Other",
        })

    else:  # Admin, superuser ou enseignant
        staff = User.objects.filter(is_lecturer=True)
        context["staff"] = staff

    return render(request, "accounts/profile.html", context)

@login_required
@admin_required
def profile_single(request, user_id):
    """Display profile of any user (admin only), optional PDF download"""
    if request.user.id == user_id:
        return redirect("profile")

    user = get_object_or_404(User, pk=user_id)
    context = {
        "title": user.get_full_name(),
        "user": user,
    }

    if user.is_lecturer:
        context.update({"user_type": "Lecturer"})

    elif user.is_student:
        student = get_object_or_404(Student, student__pk=user_id)
        parent = Parent.objects.filter(student=student).first()
        context.update({
            "user_type": "Student",
            "student": student,
            "parent": parent,
        })

    elif user.is_parent:
        parent = get_object_or_404(Parent, parent=user)
        children = Student.objects.filter(parent=parent)
        context.update({"user_type": "Parent", "parent": parent, "children": children})

    elif user.is_other:
        context.update({"user_type": "Other"})

    else:
        context["user_type"] = "Superuser"

    if request.GET.get("download_pdf"):
        return render_to_pdf("pdf/profile_single.html", context)

    return render(request, "accounts/profile_single.html", context)


# ########################################################
# Settings Views
# ########################################################


@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        messages.error(request, "Please correct the error(s) below.")
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
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "setting/password_change.html", {"form": form})

# ----------------------------------------
# Staff / Lecturer views
# ----------------------------------------
@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST)
        if form.is_valid():
            lecturer = form.save()
            messages.success(request, f"Lecturer {lecturer.get_full_name()} added successfully.")
            return redirect("lecturer_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = StaffAddForm()
    return render(request, "accounts/add_staff.html", {"title": "Add Lecturer", "form": form})

@login_required
@admin_required
def edit_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=lecturer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lecturer {lecturer.get_full_name()} updated.")
            return redirect("lecturer_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=lecturer)
    return render(request, "accounts/edit_lecturer.html", {"title": "Edit Lecturer", "form": form})

@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, is_lecturer=True, pk=pk)
    full_name = lecturer.get_full_name()
    lecturer.delete()
    messages.success(request, f"Lecturer {full_name} deleted.")
    return redirect("lecturer_list")

# ----------------------------------------
# Student views
# ----------------------------------------
@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student.get_full_name()} added successfully.")
            return redirect("student_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = StudentAddForm()
    return render(request, "accounts/add_student.html", {"title": "Add Student", "form": form})

@login_required
@admin_required
def edit_student(request, pk):
    student_user = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student {student_user.get_full_name()} updated.")
            return redirect("student_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=student_user)
    return render(request, "accounts/edit_student.html", {"title": "Edit Student", "form": form})

@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    full_name = student.student.get_full_name()
    student.delete()
    messages.success(request, f"Student {full_name} deleted.")
    return redirect("student_list")

# ----------------------------------------
# Parent views
# ----------------------------------------
@method_decorator([login_required, admin_required], name="dispatch")
class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = "accounts/parent_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Parent added successfully.")
        return super().form_valid(form)

@login_required
@admin_required
def edit_parent(request, pk):
    parent_obj = get_object_or_404(Parent, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=parent_obj.parent)
        if form.is_valid():
            form.save()
            messages.success(request, f"Parent {parent_obj.parent.get_full_name()} updated.")
            return redirect("parent_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=parent_obj.parent)
    return render(request, "accounts/edit_parent.html", {"title": "Edit Parent", "form": form})

@login_required
@admin_required
def delete_parent(request, pk):
    parent_obj = get_object_or_404(Parent, pk=pk)
    full_name = parent_obj.parent.get_full_name()
    user = parent_obj.parent
    parent_obj.delete()
    user.delete()
    messages.success(request, f"Parent {full_name} deleted.")
    return redirect("parent_list")

# ----------------------------------------
# Other users views
# ----------------------------------------
@login_required
@admin_required
def other_add_view(request):
    if request.method == "POST":
        form = OtherAddForm(request.POST)
        if form.is_valid():
            other_user = form.save()
            messages.success(request, f"Other user {other_user.get_full_name()} added successfully.")
            return redirect("other_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = OtherAddForm()
    return render(request, "accounts/add_other.html", {"title": "Add Other User", "form": form})

@login_required
@admin_required
def edit_other(request, pk):
    other_user = get_object_or_404(User, is_other=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=other_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Other user {other_user.get_full_name()} updated.")
            return redirect("other_list")
        messages.error(request, "Correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=other_user)
    return render(request, "accounts/edit_other.html", {"title": "Edit Other User", "form": form})

@login_required
@admin_required
def delete_other(request, pk):
    other_user = get_object_or_404(User, is_other=True, pk=pk)
    full_name = other_user.get_full_name()
    other_user.delete()
    messages.success(request, f"Other user {full_name} deleted.")
    return redirect("other_list")

@login_required
@admin_required
def other_list(request):
    others = User.objects.filter(is_other=True)
    return render(request, "accounts/other_list.html", {"others": others, "title": "Other Users List"})

# ----------------------------------------
# Teacher Info / Fiche views
# ----------------------------------------
@login_required
def teacher_info_add(request):
    user = request.user

    # Crée le Teacher si nécessaire
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
            messages.success(request, "Teacher information sheet saved.")
            return redirect("teacher_info_pdf", pk=info.pk)
        messages.error(request, "Correct the errors below.")
    else:
        form = TeacherInfoForm()
    
    return render(request, "accounts/teacher_info_form.html", {"title": "Teacher Info", "form": form})

@login_required
def teacher_info_edit(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    if request.method == "POST":
        form = TeacherInfoForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher info updated.")
            return redirect("profile_single", user_id=info.teacher.user.id)
        messages.error(request, "Correct the errors below.")
    else:
        form = TeacherInfoForm(instance=info)
    return render(request, "accounts/teacher_info_form.html", {"title": "Edit Teacher Info", "form": form})

@login_required
def teacher_info_delete(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    teacher_name = info.teacher.user.get_full_name()
    info.delete()
    messages.success(request, f"Teacher info for {teacher_name} deleted.")
    return redirect("profile_single", user_id=info.teacher.user.id)

@login_required
def teacher_info_pdf(request, pk):
    info = get_object_or_404(TeacherInfo, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_repetiteur_{info.nom}_{info.prenom}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    width, height = A4
    p = canvas.Canvas(response, pagesize=A4)

    # === Watermark discret ===
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
        ("Personne à contacter", f"{info.personne_urgence or ''} "),
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
# Lecturer filter & list
# ----------------------------------------
@method_decorator([login_required, admin_required], name="dispatch")
class LecturerFilterView(FilterView):
    model = User
    filterset_class = LecturerFilter
    template_name = "accounts/lecturer_list.html"
    context_object_name = "filter"
    
    def get_queryset(self):
        return User.objects.filter(is_lecturer=True)

# ----------------------------------------
# Student filter & list
# ----------------------------------------
@method_decorator([login_required, admin_required], name="dispatch")
class StudentFilterView(FilterView):
    model = Student
    filterset_class = StudentFilter
    template_name = "accounts/student_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        return Student.objects.all()

# ----------------------------------------
# Other users filter & list
# ----------------------------------------
@method_decorator([login_required, admin_required], name="dispatch")
class OtherFilterView(FilterView):
    model = User
    filterset_class = OtherFilter  # Correction: Ajout explicite de filterset_class
    template_name = "accounts/other_list.html"
    context_object_name = "filter"

    def get_queryset(self):
        queryset = User.objects.filter(is_other=True)
        self.filter = OtherFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

# ----------------------------------------
# Parent filter & list
# ----------------------------------------
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
# Parent list view (simple)
# ----------------------------------------
@login_required
@admin_required
def parent_list(request):
    parents = Parent.objects.select_related('parent', 'student__student').all()
    return render(request, "accounts/parent_list.html", {"parents": parents, "title": "Liste des Parents"})

# ----------------------------------------
# Export lecturers list to PDF
# ----------------------------------------
@login_required
@admin_required
def render_lecturer_pdf_list(request):
    lecturers = User.objects.filter(is_lecturer=True)
    context = {"lecturers": lecturers, "title": "Lecturers List"}
    return render_to_pdf("pdf/lecturer_list.html", context)

# ----------------------------------------
# Export students list to PDF
# ----------------------------------------
@login_required
@admin_required
def render_student_pdf_list(request):
    students = Student.objects.all()
    context = {"students": students, "title": "Students List"}
    return render_to_pdf("pdf/student_list.html", context)

# ----------------------------------------
# Export other users list to PDF
# ----------------------------------------
@login_required
@admin_required
def render_other_pdf_list(request):
    others = User.objects.filter(is_other=True)
    context = {"others": others, "title": "Other Users List"}
    return render_to_pdf("pdf/other_list.html", context)

# ----------------------------------------
# Export parents list to PDF
# ----------------------------------------
@login_required
@admin_required
def render_parent_pdf_list(request):
    parents = Parent.objects.select_related('parent', 'student__student').all()
    context = {"parents": parents, "title": "Liste des Parents"}
    return render_to_pdf("pdf/parent_list.html", context)