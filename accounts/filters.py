from django.db.models import Q
import django_filters
from django_filters import FilterSet, CharFilter, ChoiceFilter
from django.db import models  # Ajout pour gérer ImageField
from .models import User, Student, Parent, Teacher, Level
from .constants import GENDERS, RELATION_SHIP

# -----------------------------
# Lecturer Filter
# -----------------------------
class LecturerFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="username", lookup_expr="exact", label="")
    name = django_filters.CharFilter(method="filter_by_name", label="")
    email = django_filters.CharFilter(lookup_expr="icontains", label="")

    class Meta:
        model = User
        fields = ["username", "email"]
        # Surcharge pour ImageField afin d'éviter les erreurs
        filter_overrides = {
            models.ImageField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["username"].field.widget.attrs.update({"class": "au-input", "placeholder": "N° d'identification"})
        self.filters["name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom"})
        self.filters["email"].field.widget.attrs.update({"class": "au-input", "placeholder": "Email"})

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))

# -----------------------------
# Student Filter
# -----------------------------
class StudentFilter(django_filters.FilterSet):
    id_no = django_filters.CharFilter(field_name="student__username", lookup_expr="exact", label="")
    name = django_filters.CharFilter(method="filter_by_name", label="")
    email = django_filters.CharFilter(field_name="student__email", lookup_expr="icontains", label="")
    program = django_filters.CharFilter(field_name="program__title", lookup_expr="icontains", label="")
    level = django_filters.CharFilter(field_name="level__name", lookup_expr="icontains", label="")

    class Meta:
        model = Student
        fields = ["id_no", "name", "email", "program", "level"]
        # Surcharge pour ImageField
        filter_overrides = {
            models.ImageField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["id_no"].field.widget.attrs.update({"class": "au-input", "placeholder": "N° d'identification"})
        self.filters["name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom"})
        self.filters["email"].field.widget.attrs.update({"class": "au-input", "placeholder": "Email"})
        self.filters["program"].field.widget.attrs.update({"class": "au-input", "placeholder": "Programme"})
        self.filters["level"].field.widget.attrs.update({"class": "au-input", "placeholder": "Niveau"})

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__first_name__icontains=value) | Q(student__last_name__icontains=value)
        )

# -----------------------------
# Parent Filter
# -----------------------------
class ParentFilter(django_filters.FilterSet):
    parent__username = django_filters.CharFilter(
        field_name='parent__username', 
        lookup_expr='icontains',
        label='Nom d\'utilisateur'
    )
    parent__first_name = django_filters.CharFilter(
        field_name='parent__first_name', 
        lookup_expr='icontains',
        label='Prénom'
    )
    parent__last_name = django_filters.CharFilter(
        field_name='parent__last_name', 
        lookup_expr='icontains',
        label='Nom'
    )
    parent__email = django_filters.CharFilter(
        field_name='parent__email', 
        lookup_expr='icontains',
        label='Email'
    )
    relation_ship = django_filters.ChoiceFilter(
        choices=RELATION_SHIP,
        label='Relation',
        empty_label='Toutes les relations'
    )

    class Meta:
        model = Parent
        fields = [
            'parent__username',
            'parent__first_name', 
            'parent__last_name',
            'parent__email',
            'relation_ship'
        ]
        # Surcharge pour ImageField
        filter_overrides = {
            models.ImageField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["parent__username"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom d'utilisateur"})
        self.filters["parent__first_name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Prénom"})
        self.filters["parent__last_name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom"})
        self.filters["parent__email"].field.widget.attrs.update({"class": "au-input", "placeholder": "Email"})
        self.filters["relation_ship"].field.widget.attrs.update({"class": "au-input", "placeholder": "Relation"})

# -----------------------------
# Other Users Filter
# -----------------------------
class OtherFilter(FilterSet):
    username = CharFilter(
        field_name='username', 
        lookup_expr='icontains',
        label='Nom d\'utilisateur'
    )
    first_name = CharFilter(
        field_name='first_name', 
        lookup_expr='icontains',
        label='Prénom'
    )
    last_name = CharFilter(
        field_name='last_name', 
        lookup_expr='icontains',
        label='Nom'
    )
    email = CharFilter(
        field_name='email', 
        lookup_expr='icontains',
        label='Email'
    )
    phone = CharFilter(
        field_name='phone', 
        lookup_expr='icontains',
        label='Téléphone'
    )
    gender = ChoiceFilter(
        choices=GENDERS,
        label='Genre',
        empty_label='Tous les genres'
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name', 
            'last_name',
            'email',
            'phone',
            'gender'
        ]
        # Exclure explicitement le champ picture
        exclude = ['picture']
        # Surcharge pour ImageField pour éviter l'erreur
        filter_overrides = {
            models.ImageField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mettre à jour les attributs des champs pour le style
        self.filters["username"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom d'utilisateur"})
        self.filters["first_name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Prénom"})
        self.filters["last_name"].field.widget.attrs.update({"class": "au-input", "placeholder": "Nom"})
        self.filters["email"].field.widget.attrs.update({"class": "au-input", "placeholder": "Email"})
        self.filters["phone"].field.widget.attrs.update({"class": "au-input", "placeholder": "Téléphone"})
        self.filters["gender"].field.widget.attrs.update({"class": "au-input", "placeholder": "Genre"})
        
        # Filtrer uniquement les utilisateurs de type "other"
        self.queryset = User.objects.filter(is_other=True)