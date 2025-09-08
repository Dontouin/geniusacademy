from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from .models import User, Student, Parent, RELATION_SHIP, Level, GENDERS,TeacherInfo,Teacher

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

class UserCreationForm(forms.ModelForm):
    """Formulaire pour créer un nouvel utilisateur avec mot de passe"""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# -----------------------------
# Formulaire ajout du staff (enseignant)
# -----------------------------
class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"type": "text", "class": "form-control"}),
        label="Nom d'utilisateur",
    )
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom")
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom")
    gender = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-control"}), label="Genre")
    address = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    password1 = forms.CharField(max_length=30, required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Mot de passe")
    password2 = forms.CharField(max_length=30, required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmation du mot de passe")

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

# -----------------------------
# Formulaire ajout d'un étudiant
# -----------------------------
class StudentAddForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom d'utilisateur")
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom")
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom")
    gender = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-control"}), label="Genre")
    level = forms.ChoiceField(choices=Level, widget=forms.Select(attrs={"class": "form-control"}), label="Niveau")
    address = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    password1 = forms.CharField(max_length=30, required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Mot de passe")
    password2 = forms.CharField(max_length=30, required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmation du mot de passe")

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            Student.objects.create(
                student=user,
                level=self.cleaned_data.get("level"),
            )
        return user

# -----------------------------
# Formulaire mise à jour du profil utilisateur
# -----------------------------
class ProfileUpdateForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom")
    gender = forms.ChoiceField(choices=GENDERS, widget=forms.Select(attrs={"class": "form-control"}), label="Genre")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "gender", "email", "phone", "address", "picture"]

# -----------------------------
# Validation de l'email pour mot de passe oublié
# -----------------------------
class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error(
                "email",
                "Aucun utilisateur n'est enregistré avec cette adresse e-mail."
            )
        return email

# -----------------------------
# Formulaire ajout parent
# -----------------------------
class ParentAddForm(forms.ModelForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom d'utilisateur"
    )
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom")
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    address = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Étudiant",
        required=False,
        empty_label="--- Sélectionner un étudiant ---"
    )
    relation_ship = forms.ChoiceField(
        choices=RELATION_SHIP,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Relation",
        required=False
    )
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Mot de passe")
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmation du mot de passe")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "address", "phone"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        
        # Définir le mot de passe
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            # TOUJOURS créer l'objet Parent, mais student peut être null
            Parent.objects.create(
                parent=user,
                student=self.cleaned_data.get("student"),  # Peut être None
                relation_ship=self.cleaned_data.get("relation_ship", ""),
            )
        return user
# -----------------------------
# Formulaire ajout Enseignant
# -----------------------------
class TeacherAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom d'utilisateur",
        required=False,
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Prénom",
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom",
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
    )
    address = forms.CharField(max_length=60, widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    speciality = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}), label="Spécialité")
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Mot de passe")
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmation du mot de passe")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "gender", "address", "phone"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                speciality=self.cleaned_data.get("speciality"),
            )
        return user

# -----------------------------
# Formulaire Info Enseignant
# -----------------------------
class TeacherInfoForm(forms.ModelForm):
    class Meta:
        model = TeacherInfo
        fields = [
            "nom", "prenom", "date_naissance", "lieu_naissance", "sexe", 
            "nationalite", "statut_matrimonial", "adresse", "cni_numero",
            "email", "contact", "personne_urgence", "contact_urgence", 
            "photo", "section_enseignement", "domaine_enseignement", 
            "niveau_scolaire", "diplome", "marge_enseignement", 
            "matieres_primaire", "matieres_secondaire", "experience"
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sexe": forms.Select(attrs={"class": "form-select"}),
            "statut_matrimonial": forms.Select(attrs={"class": "form-select"}),
            "adresse": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre adresse complète"}),
            "cni_numero": forms.TextInput(attrs={"class": "form-control", "placeholder": "Numéro CNI ou récépissé"}),
            "contact_urgence": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
            "experience": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "matieres_primaire": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "matieres_secondaire": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

# -----------------------------
# Mise à jour profil utilisateur (version alternative)
# -----------------------------
class ProfileUpdateFormAlt(UserChangeForm):
    password = None  # Exclure le champ mot de passe

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom"
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom"
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    picture = forms.ImageField(required=False, label="Photo")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "gender", "email", "phone", "address", "picture"]

# -----------------------------
# Validation email pour mot de passe oublié (version alternative)
# -----------------------------
class EmailValidationOnForgotPasswordAlt(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "Aucun utilisateur n'est enregistré avec cette adresse e-mail."
            self.add_error("email", msg)
        return email

# -----------------------------
# Formulaire ajout Parent (version alternative)
# -----------------------------
class ParentAddFormAlt(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom d'utilisateur")
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Prénom")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Nom")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Adresse")
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Téléphone")
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Étudiant",
    )
    relation_ship = forms.ChoiceField(
        choices=RELATION_SHIP,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Relation avec l'étudiant",
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmation du mot de passe")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "address", "phone"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            Parent.objects.create(
                user=user,
                student=self.cleaned_data.get("student"),
                relation_ship=self.cleaned_data.get("relation_ship"),
            )
        return user