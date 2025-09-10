from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from PIL import Image
from django.core.validators import FileExtensionValidator
import os
from django.utils.crypto import get_random_string

# -----------------------------
# Constantes et choix
# -----------------------------
PERE = _("Père")
MERE = _("Mère")
FRERE = _("Frère")
SOEUR = _("Sœur")
GRAND_MERE = _("Grand-mère")
GRAND_PERE = _("Grand-père")
AUTRE = _("Autre")

RELATION_SHIP = (
    (PERE, _("Père")),
    (MERE, _("Mère")),
    (FRERE, _("Frère")),
    (SOEUR, _("Sœur")),
    (GRAND_MERE, _("Grand-mère")),
    (GRAND_PERE, _("Grand-père")),
    (AUTRE, _("Autre")),
)

GENDERS = ((_("M"), _("Masculin")), (_("F"), _("Féminin")))

STATUT_MATRIMONIAL = (
    ("single", _("Célibataire")),
    ("married", _("Marié(e)")),
    ("divorced", _("Divorcé(e)")),
    ("widowed", _("Veuf(ve)")),
)

# -----------------------------
# Custom User Manager
# -----------------------------
class CustomUserManager(UserManager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            qs = qs.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            ).distinct()
        return qs

    def get_student_count(self):
        return self.get_queryset().filter(is_student=True).count()

    def get_lecturer_count(self):
        return self.get_queryset().filter(is_lecturer=True).count()

    def get_superuser_count(self):
        return self.get_queryset().filter(is_superuser=True).count()

    def make_random_password(
        self,
        length: int = 5,  # 5 chiffres
        allowed_chars: str = "0123456789"  # uniquement des chiffres
    ) -> str:
        return get_random_string(length, allowed_chars)

# -----------------------------
# User model
# -----------------------------
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    is_other = models.BooleanField(default=False)  # Nouveau type d'utilisateur
    
    matricule = models.CharField(max_length=50, blank=True, null=True, unique=True)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=120, blank=True, null=True)
    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True, blank=True
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    def save(self, *args, **kwargs):
        # NE générer un matricule QUE pour les enseignants
        if not self.matricule and self.is_lecturer:
            from accounts.utils import generate_lecturer_id
            self.matricule = generate_lecturer_id()
        
        # Pour tous les autres types (étudiants, parents, autres), NE PAS générer de matricule
        # Ils peuvent avoir un matricule manuel ou rester sans matricule
        
        super().save(*args, **kwargs)

        if self.picture and os.path.exists(self.picture.path):
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.picture.path)

    # Méthodes utiles pour AdminRole
    def is_admin_role(self, role_name):
        return hasattr(self, "admin_role") and self.admin_role.role == role_name

    @property
    def admin_role_name(self):
        return self.admin_role.get_role_display() if hasattr(self, "admin_role") else None

# -----------------------------
# Admin Role model
# -----------------------------
class AdminRole(models.Model):
    ROLE_CHOICES = [
        ("super_admin", _("Super Administrateur")),
        ("academic_admin", _("Admin Académique")),
        ("secretary", _("Secrétaire")),
        ("finance", _("Comptable")),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_role")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Rôle Administrateur")
        verbose_name_plural = _("Rôles Administrateurs")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

# -----------------------------
# Level model
# -----------------------------
Level = [
    ('Primary', _('Primaire')),
    ('Secondary', _('Secondaire')),
    ('High', _('Lycée')),
]

# -----------------------------
# Student model
# -----------------------------
class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            qs = qs.filter(Q(level__icontains=query) | Q(program__name__icontains=query)).distinct()
        return qs

class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=Level, null=True)
   
    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        return self.student.get_full_name()

    @classmethod
    def get_gender_count(cls):
        return {
            'M': cls.objects.filter(student__gender='M').count(),
            'F': cls.objects.filter(student__gender='F').count()
        }

    @classmethod
    def get_total_students(cls):
        return cls.objects.count()

# -----------------------------
# Parent model
# -----------------------------
class Parent(models.Model):
    parent = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    relation_ship = models.CharField(max_length=50, choices=RELATION_SHIP, blank=True)

    def __str__(self):
        return self.parent.get_full_name()

# -----------------------------
# Teacher model
# -----------------------------
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=255)
    diploma = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.speciality}"

# -----------------------------
# Teacher Info / Fiche Enseignant
# -----------------------------
def fiche_upload_path(instance, filename):
    return f"fiche_teachers/{instance.teacher.user.username}/{filename}"

class TeacherInfo(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="info")
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=255)
    sexe = models.CharField(max_length=10, choices=(('M', 'Masculin'), ('F', 'Féminin')), null=True, blank=True)
    nationalite = models.CharField(max_length=100, null=True, blank=True)
    statut_matrimonial = models.CharField(max_length=20, choices=STATUT_MATRIMONIAL)
    email = models.EmailField()
    contact = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    cni_numero = models.CharField(max_length=100, blank=True, null=True)
    contact_urgence = models.CharField(max_length=50, blank=True, null=True)
    personne_urgence = models.CharField(max_length=255)
    cont_urgence = models.CharField(max_length=50)
    photo = models.ImageField(
        upload_to=fiche_upload_path,
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])]
    )
    section_enseignement = models.CharField(max_length=255)
    domaine_enseignement = models.CharField(
        max_length=255,
        choices=(
            ('Scientifique', _('Scientifique')),
            ('Littéraire', _('Littéraire')),
        ),
        null=True, blank=True
    )
    niveau_scolaire = models.CharField(max_length=255, null=True, blank=True)
    diplome = models.CharField(max_length=255)
    marge_enseignement = models.CharField(max_length=255, blank=True, null=True)
    matieres_primaire = models.TextField(blank=True, null=True)
    matieres_secondaire = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def matricule(self):
        return self.teacher.user.matricule if hasattr(self.teacher.user, 'matricule') else None

    def __str__(self):
        return f"Fiche de {self.teacher.user.get_full_name()} ({self.matricule})"

# -----------------------------
# ActivityLog model
# -----------------------------
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.get_full_name() if self.user else 'Système'} - {self.message[:30]}"

# -----------------------------
# Classe model
# -----------------------------
class Classe(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nom de la classe"))

    class Meta:
        verbose_name = _("Classe")
        verbose_name_plural = _("Classes")

    def __str__(self):
        return self.name