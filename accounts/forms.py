from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.db import transaction
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, Student, Parent, RELATION_SHIP, Level, GENDERS, TeacherInfo, Teacher



# Custom UserCreationForm (renamed to avoid confusion with Django's UserCreationForm)
class CustomUserCreationForm(forms.ModelForm):
    """Formulaire pour créer un nouvel utilisateur avec mot de passe."""
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# -----------------------------
# Formulaire ajout d'un étudiant
# -----------------------------
class StudentAddForm(UserCreationForm):
    """Formulaire pour ajouter un étudiant."""
    username = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}),
        label="Nom d'utilisateur",
        help_text="Optionnel. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ seulement."
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
        required=True
    )
    level = forms.ChoiceField(
        choices=Level,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Niveau scolaire",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
        label="Mot de passe",
        required=False
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
        label="Confirmation du mot de passe",
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'phone', 'address', 'level']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        if (password1 and not password2) or (password2 and not password1):
            raise forms.ValidationError("Veuillez remplir les deux champs de mot de passe.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.is_staff = False
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Student.objects.create(
                student=user,
                level=self.cleaned_data.get("level"),
            )
        return user
    
class StaffAddForm(UserCreationForm):
    """Formulaire pour ajouter un membre du staff."""
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}),
        label="Nom d'utilisateur",
        required=True
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
        label="Mot de passe",
        required=True
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
        label="Confirmation du mot de passe",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'address', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# -----------------------------
# Formulaire ajout parent
# -----------------------------
class ParentAddForm(CustomUserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}),
        label="Nom d'utilisateur",
        required=False,
        help_text="Optionnel. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ seulement."
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
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
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
        label="Mot de passe",
        required=True
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
        label="Confirmation du mot de passe",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'address', 'phone', 'student', 'relation_ship']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_parent = True
        user.is_staff = False
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            Parent.objects.create(
                parent=user,
                student=self.cleaned_data.get("student"),
                relation_ship=self.cleaned_data.get("relation_ship", ""),
            )
        return user

# -----------------------------
# Formulaire ajout Enseignant
# -----------------------------
class TeacherAddForm(UserCreationForm):
    """Formulaire pour ajouter un enseignant."""
    username = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}),
        label="Nom d'utilisateur",
        help_text="Optionnel. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ seulement."
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    speciality = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Mathématiques, Littérature"}),
        label="Spécialité",
        required=True
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
        label="Mot de passe",
        required=True
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
        label="Confirmation du mot de passe",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'phone', 'speciality']

    def clean_email(self):
        """Vérifie que l'email est unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        """Valide le format du numéro de téléphone."""
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

    def clean(self):
        """Valide que les mots de passe correspondent."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.is_staff = False
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                speciality=self.cleaned_data.get("speciality"),
            )
        return user

# -----------------------------
# Formulaire ajout d'un utilisateur générique
# -----------------------------
class OtherAddForm(UserCreationForm):
    """Formulaire pour ajouter un utilisateur générique."""
    username = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}),
        label="Nom d'utilisateur",
        help_text="Optionnel. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ seulement."
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
        label="Mot de passe",
        required=True
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmez le mot de passe"}),
        label="Confirmation du mot de passe",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'phone', 'address']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_other = True
        user.is_staff = False
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
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
# Mise à jour profil utilisateur
# -----------------------------
class ProfileUpdateForm(UserChangeForm):
    password = None
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
        label="Prénom",
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        label="Nom",
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Genre",
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adresse@example.com"}),
        label="Email",
        required=True
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: +237 6xx xx xx xx"}),
        label="Téléphone",
        required=True
    )
    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adresse complète"}),
        label="Adresse",
        required=True
    )
    picture = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Photo de profil",
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'email', 'phone', 'address', 'picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+') or len(phone) < 10:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +237 6xx xx xx xx).")
        return phone

# -----------------------------
# Validation email pour mot de passe oublié
# -----------------------------
class EmailValidationOnForgotPasswordAlt(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("Aucun utilisateur n'est enregistré avec cette adresse e-mail.")
        return email