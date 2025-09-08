# models.py
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, Student, Parent
from django.urls import reverse


NEWS = _("News")
EVENTS = _("Event")

POST = (
    (NEWS, _("News")),
    (EVENTS, _("Event")),
)

FIRST = _("First")
SECOND = _("Second")
THIRD = _("Third")

SEMESTER = (
    (FIRST, _("First")),
    (SECOND, _("Second")),
    (THIRD, _("Third")),
)


class NewsAndEventsQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(posted_as__icontains=query)
        )
        return self.filter(lookups).distinct()


class NewsAndEventsManager(models.Manager):
    def get_queryset(self):
        return NewsAndEventsQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(
            id=id
        )  # NewsAndEvents.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)


class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True)
    summary = models.TextField(max_length=200, blank=True, null=True)
    posted_as = models.CharField(choices=POST, max_length=10)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    objects = NewsAndEventsManager()

    def __str__(self):
        return f"{self.title}"



class ActivityLog(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.created_at}]{self.message}"

class SuccessRate(models.Model):
    year = models.PositiveIntegerField(unique=True)
    rate = models.PositiveIntegerField()  # % de réussite, entre 0 et 100
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.year}: {self.rate}%"

    @classmethod
    def get_latest(cls):
        """Retourne le dernier taux enregistré."""
        return cls.objects.order_by('-year').first()


###############################################################################################################################################
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str  # pour convertir les lazy proxy en str


# ---------------- NEWSLETTER ----------------
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name=_("Adresse email"))
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Nom"))
    source = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Source"))
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date d'inscription"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    class Meta:
        verbose_name = _("Abonné à la newsletter")
        verbose_name_plural = _("Abonnés à la newsletter")

    def __str__(self):
        return force_str(self.email)


# ---------------- CAROUSEL / GALLERY ----------------
class Slide(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name=_("Titre"))
    tag = models.CharField(max_length=100, blank=True, verbose_name=_("Étiquette"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

    class Meta:
        ordering = ["order"]
        verbose_name = _("Diapositive")
        verbose_name_plural = _("Diapositives")

    def __str__(self):
        return force_str(self.title or f"Slide #{self.pk}")


class GalleryImage(models.Model):
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name="images", verbose_name=_("Slide"))
    image = models.ImageField(upload_to="gallery/", verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_("Texte alternatif"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    primary_cta = models.CharField(max_length=100, blank=True, verbose_name=_("Appel à l'action principal"))
    primary_link = models.CharField(max_length=200, blank=True, verbose_name=_("Lien principal"))
    secondary_cta = models.CharField(max_length=100, blank=True, verbose_name=_("Appel à l'action secondaire"))
    secondary_link = models.CharField(max_length=200, blank=True, verbose_name=_("Lien secondaire"))
    secondary_icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icône secondaire"))

    class Meta:
        ordering = ["order"]
        verbose_name = _("Image du carrousel")
        verbose_name_plural = _("Images du carrousel")

    def get_alt_text(self):
        return force_str(self.alt_text or _("Image de la galerie"))

    def __str__(self):
        return force_str(self.alt_text or _("Image de la galerie"))


# ---------------- TESTIMONIAL ----------------
class Testimonial(models.Model):
    # Types de témoignages
    STUDENT = 'student'
    PARENT = 'parent'
    TEACHER = 'teacher'
    OTHER = 'other'
    
    TESTIMONIAL_TYPE_CHOICES = (
        (STUDENT, _('Élève')),
        (PARENT, _('Parent')),
        (TEACHER, _('Enseignant')),
        (OTHER, _('Autre')),
    )
    
    # Lien à l'utilisateur si connecté
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Utilisateur")
    )
    
    # Informations de base
    author = models.CharField(max_length=100, verbose_name=_("Auteur"))
    testimonial_type = models.CharField(
        max_length=10, 
        choices=TESTIMONIAL_TYPE_CHOICES,
        default=STUDENT,
        verbose_name=_("Type de témoignage")
    )
    
    # Pour les parents : nom de l'enfant
    child_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_("Nom de l'enfant")
    )
    
    # Pour les enseignants : matière enseignée
    subject_taught = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_("Matière enseignée")
    )
    
    # Contenu et évaluation
    content = models.TextField(max_length=500, verbose_name=_("Contenu"))
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name=_("Note (1-5 étoiles)")
    )
    
    # Pour lier à des étudiants ou parents spécifiques
    student = models.ForeignKey(
        Student, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Élève concerné")
    )
    
    parent = models.ForeignKey(
        Parent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Parent concerné")
    )
    
    # Media et métadonnées
    image = models.ImageField(
        upload_to="testimonials/", 
        blank=True, 
        null=True, 
        verbose_name=_("Photo de l'auteur")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Date de création")
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("Actif")
    )
    
    is_approved = models.BooleanField(
        default=False, 
        verbose_name=_("Approuvé")
    )
    
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Ordre d'affichage")
    )
    
    # Champs pour les statistiques d'engagement
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de 'utile'")
    )
    
    featured = models.BooleanField(
        default=False,
        verbose_name=_("Témoignage en vedette")
    )

    class Meta:
        verbose_name = _("Témoignage")
        verbose_name_plural = _("Témoignages")
        ordering = ["-featured", "order", "-created_at"]

    def __str__(self):
        return force_str(f"{self.author} - {self.content[:50]}...")
    
    def save(self, *args, **kwargs):
        # Si un utilisateur est lié, compléter automatiquement les informations
        if self.user:
            if not self.author:
                self.author = self.user.get_full_name()
            
            # Déterminer automatiquement le type de témoignage
            if not self.testimonial_type:
                if self.user.is_student:
                    self.testimonial_type = self.STUDENT
                elif self.user.is_parent:
                    self.testimonial_type = self.PARENT
                elif self.user.is_lecturer:
                    self.testimonial_type = self.TEACHER
        
        super().save(*args, **kwargs)
    
    @property
    def author_initials(self):
        """Retourne les initiales de l'auteur"""
        if not self.author:
            return "NN"
        names = self.author.split()
        if len(names) >= 2:
            return f"{names[0][0]}{names[-1][0]}".upper()
        return self.author[:2].upper()
    
    @property
    def excerpt(self):
        """Retourne un extrait du témoignage"""
        if len(self.content) <= 150:
            return self.content
        return self.content[:147] + "..."
    
    def get_absolute_url(self):
        """URL pour accéder au témoignage individuel"""
        return reverse('testimonial_detail', kwargs={'pk': self.pk})
    
    def get_type_display(self):
        """Retourne le type affiché avec icône"""
        type_icons = {
            self.STUDENT: "👨‍🎓",
            self.PARENT: "👨‍👩‍👧‍👦", 
            self.TEACHER: "👨‍🏫",
            self.OTHER: "👤"
        }
        return f"{type_icons.get(self.testimonial_type, '👤')} {self.get_testimonial_type_display()}"
    
    def get_rating_stars(self):
        """Retourne le HTML pour afficher les étoiles de notation"""
        full_stars = self.rating
        empty_stars = 5 - full_stars
        
        stars_html = ''
        for i in range(full_stars):
            stars_html += '<i class="fas fa-star text-warning"></i>'
        for i in range(empty_stars):
            stars_html += '<i class="far fa-star text-warning"></i>'
            
        return stars_html
    
    def get_display_name(self):
        """Retourne le nom d'affichage approprié selon le type"""
        if self.testimonial_type == self.PARENT and self.child_name:
            return f"{self.author} (Parent de {self.child_name})"
        elif self.testimonial_type == self.TEACHER and self.subject_taught:
            return f"{self.author} ({self.subject_taught})"
        else:
            return self.author


# ---------------- CONTACT ----------------
LEVEL_CHOICES = (
    ("Maternelle", _("Maternelle")),
    ("Primaire", _("Primaire")),
    ("Collège", _("Collège")),
    ("Lycée", _("Lycée")),
)

class ContactMessage(models.Model):
    nom = models.CharField(max_length=100, verbose_name=_("Nom complet"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Téléphone"))
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True, verbose_name=_("Niveau scolaire"))
    sujet = models.CharField(max_length=150, verbose_name=_("Sujet"))
    message = models.TextField(verbose_name=_("Message"))
    newsletter = models.BooleanField(default=False, verbose_name=_("S'abonner à la newsletter"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date d'envoi"))
    is_read = models.BooleanField(default=False, verbose_name=_("Lu"))

    class Meta:
        verbose_name = _("Message de contact")
        verbose_name_plural = _("Messages de contact")
        ordering = ["-created_at"]

    def __str__(self):
        return force_str(f"{self.nom} - {self.sujet}")

from django.db import models
from django.utils.translation import gettext_lazy as _

class StatValue(models.Model):
    name = models.CharField(_("Nom"), max_length=50, unique=True)
    value = models.PositiveIntegerField(_("Valeur"))

    class Meta:
        verbose_name = _("Valeur de statistique")
        verbose_name_plural = _("Valeurs de statistiques")

    def __str__(self):
        return f"{self.name}: {self.value}"
# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class AcademicEvent(models.Model):
    date = models.DateField(verbose_name=_("Date"))
    activity = models.CharField(max_length=255, verbose_name=_("Activité"))
    responsible = models.CharField(max_length=255, verbose_name=_("Responsable"))

    class Meta:
        ordering = ["date"]
        verbose_name = _("Événement académique")
        verbose_name_plural = _("Événements académiques")

    def __str__(self):
        return f"{self.date} - {self.activity}"


from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# -------------------------------
# Absences enseignants
# -------------------------------
class Absence(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="absences")
    date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("Absence")
        verbose_name_plural = _("Absences")
        ordering = ['date']

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.date}"


# -------------------------------
# Réservations de cours
# -------------------------------
class Reservation(models.Model):
    course_name = models.CharField(max_length=255)
    student_name = models.CharField(max_length=150)
    date = models.DateField()

    class Meta:
        verbose_name = _("Réservation")
        verbose_name_plural = _("Réservations")
        ordering = ['date']

    def __str__(self):
        return f"{self.course_name} - {self.student_name} - {self.date}"
