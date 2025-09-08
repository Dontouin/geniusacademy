from django import forms
from .models import NewsAndEvents ,ContactMessage,LEVEL_CHOICES


# news and events
class NewsAndEventsForm(forms.ModelForm):
    class Meta:
        model = NewsAndEvents
        fields = (
            "title",
            "summary",
            "posted_as",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["posted_as"].widget.attrs.update({"class": "form-control"})


############################################################################
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import NewsletterSubscriber, Testimonial

class NewsletterForm(forms.ModelForm):
    """Formulaire pour l'inscription à la newsletter."""
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border rounded bg-gray-50 text-gray-800 placeholder-gray-400',
                'placeholder': _("Entrez votre email")
            })
        }
        labels = {
            'email': _("Adresse email")
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(_("Cet email est déjà abonné à la newsletter."))
        return email

# forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    """Formulaire amélioré pour soumettre un témoignage."""
    
    # Champ supplémentaire pour la confirmation des parents
    is_parent_confirmation = forms.BooleanField(
        required=False,
        label=_("Je suis parent d'un élève de The Genius Academy"),
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is-parent-checkbox'
        })
    )
    
    class Meta:
        model = Testimonial
        fields = [
            'author', 'testimonial_type', 'child_name', 
            'subject_taught', 'rating', 'content', 'image'
        ]
        
        widgets = {
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Votre nom complet")
            }),
            'testimonial_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'testimonial-type'
            }),
            'child_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Nom de votre enfant"),
                'id': 'child-name-field'
            }),
            'subject_taught': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Matière enseignée"),
                'id': 'subject-field'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'type': 'number'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _("Partagez votre expérience avec The Genius Academy..."),
                'rows': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        
        labels = {
            'author': _("Votre nom"),
            'testimonial_type': _("Vous êtes"),
            'child_name': _("Nom de votre enfant"),
            'subject_taught': _("Matière enseignée"),
            'rating': _("Note (1-5 étoiles)"),
            'content': _("Votre témoignage"),
            'image': _("Votre photo (optionnelle)")
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-remplir avec les informations de l'utilisateur connecté
        if self.user and self.user.is_authenticated:
            if not self.instance.author:
                self.fields['author'].initial = self.user.get_full_name()
            
            # Déterminer le type par défaut selon le profil
            if self.user.is_student:
                self.fields['testimonial_type'].initial = Testimonial.STUDENT
            elif self.user.is_parent:
                self.fields['testimonial_type'].initial = Testimonial.PARENT
                self.fields['is_parent_confirmation'].initial = True
            elif self.user.is_lecturer:
                self.fields['testimonial_type'].initial = Testimonial.TEACHER
        
        # Rendre certains champs obligatoires conditionnellement
        self.fields['child_name'].required = False
        self.fields['subject_taught'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        testimonial_type = cleaned_data.get('testimonial_type')
        child_name = cleaned_data.get('child_name')
        subject_taught = cleaned_data.get('subject_taught')
        is_parent_confirmation = cleaned_data.get('is_parent_confirmation')
        
        # Validation pour les parents
        if testimonial_type == Testimonial.PARENT:
            if not child_name:
                self.add_error('child_name', _("Veuillez indiquer le nom de votre enfant."))
            
            if not is_parent_confirmation:
                self.add_error('is_parent_confirmation', 
                              _("Veuillez confirmer que vous êtes parent d'un élève."))
        
        # Validation pour les enseignants
        if testimonial_type == Testimonial.TEACHER and not subject_taught:
            self.add_error('subject_taught', _("Veuillez indiquer la matière que vous enseignez."))
        
        return cleaned_data
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 20:
            raise forms.ValidationError(_("Le témoignage doit contenir au moins 20 caractères."))
        return content
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating', 5)
        if rating < 1 or rating > 5:
            raise forms.ValidationError(_("La note doit être comprise entre 1 et 5."))
        return rating

class ContactForm(forms.ModelForm):
    newsletter = forms.BooleanField(
        required=False,
        label=_("S'abonner à la newsletter"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'phone', 'level', 'sujet', 'message', 'newsletter']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Votre nom complet")}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _("Votre email")}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Votre téléphone")}),
            'level': forms.Select(attrs={'class': 'form-select'}, choices=LEVEL_CHOICES),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Sujet de votre message")}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _("Votre message")}),
        }
        labels = {
            'nom': _("Nom complet"),
            'email': _("Email"),
            'phone': _("Téléphone"),
            'level': _("Niveau scolaire"),
            'sujet': _("Sujet"),
            'message': _("Message"),
        }

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '').strip()
        if len(nom) < 2:
            raise forms.ValidationError(_("Le nom doit contenir au moins 2 caractères."))
        return nom

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError(_("Le message doit contenir au moins 10 caractères."))
        return message

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()
    
    # core/forms.py
from django import forms
from .models import AcademicEvent
from django.utils.translation import gettext_lazy as _

RESPONSIBLE_CHOICES = [
    ("Administration", _("Administration")),
    ("Président Directeur Général", _("Président Directeur Général")),
    ("Directeur de Zone", _("Directeur de Zone")),
    ("Tout le Personnel", _("Tout le Personnel")),
    ("Jour férié", _("Jour férié")),
]

class AcademicEventForm(forms.ModelForm):
    responsible = forms.ChoiceField(
        choices=RESPONSIBLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Responsable")
    )

    class Meta:
        model = AcademicEvent
        fields = ["date", "activity", "responsible"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "activity": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Fête de Noël")}),
        }
        labels = {
            "date": _("Date de l'événement"),
            "activity": _("Activité"),
            "responsible": _("Responsable"),
        }

from django import forms
from .models import AcademicEvent, Absence, Reservation

# -------------------------------
# Formulaire Événement Académique
# -------------------------------
class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = ['date', 'activity', 'responsible']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activity': forms.TextInput(attrs={'class': 'form-control'}),
            'responsible': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Absence, Reservation
from accounts.models import Teacher, Classe  # Assure-toi que ces modèles existent

# -------------------------------
# Formulaire Absence
# -------------------------------
class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['teacher', 'date', 'reason']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }

# -------------------------------
# Formulaire Réservation
# -------------------------------
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['course_name', 'student_name', 'date']
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# -------------------------------
# Formulaire Rapport Secrétaire
# -------------------------------
REPORT_TYPE_CHOICES = [
    ('all', 'Tous les événements'),
    ('students', 'Étudiants seulement'),
    ('teachers', 'Enseignants seulement'),
    ('classes', 'Classes seulement'),
]

class SecretaryReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de début"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de fin"
    )
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type de rapport"
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe (optionnel)"
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Enseignant (optionnel)"
    )
