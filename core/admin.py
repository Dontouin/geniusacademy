from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from .models import (
    Slide, GalleryImage, Testimonial, NewsletterSubscriber, 
    ContactMessage, StatValue, NewsAndEvents, AcademicEvent,
    Absence, Reservation, SuccessRate
)

# ---------------- NewsAndEvents Admin ----------------
@admin.register(NewsAndEvents)
class NewsAndEventsAdmin(TranslationAdmin):
    list_display = ('title', 'summary', 'posted_as', 'updated_date')
    list_filter = ('posted_as', 'updated_date')
    search_fields = ('title', 'summary')
    date_hierarchy = 'updated_date'

# ---------------- Drag & Drop Inline pour les images ----------------
class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = (
        "thumbnail_preview",
        "image",
        "alt_text",
        "order",
        "primary_cta",
        "primary_link",
        "secondary_cta",
        "secondary_link",
        "secondary_icon",
    )
    readonly_fields = ["thumbnail_preview"]
    ordering = ["order"]

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px; max-width:150px;" alt="{}" />',
                obj.image.url,
                obj.get_alt_text(),
            )
        return "-"
    thumbnail_preview.short_description = _("Prévisualisation")

# ---------------- Slide Admin ----------------
@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ["image_count", "order"]
    list_editable = ["order"]
    list_display_links = ["image_count"]
    ordering = ["order"]
    inlines = [GalleryImageInline]

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = _("Nombre d'images")

# ---------------- Testimonial Admin ----------------
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["author", "content_preview", "is_active", "is_approved", "order", "created_at", "thumbnail"]
    list_editable = ["order", "is_active", "is_approved"]
    list_filter = ["is_active", "is_approved", "created_at"]
    search_fields = ["author", "content"]
    actions = ["approve_testimonials", "disapprove_testimonials"]
    readonly_fields = ["created_at", "thumbnail_preview"]
    ordering = ["order", "created_at"]
    
    fieldsets = (
        (None, {
            'fields': ('author', 'content', 'image')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_approved', 'order')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'thumbnail_preview'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = _("Aperçu du contenu")

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px; max-width:50px;" alt="{}" />', obj.image.url, obj.author)
        return "-"
    thumbnail.short_description = _("Miniature")

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px; max-width:200px;" alt="{}" />', obj.image.url, obj.author)
        return "-"
    thumbnail_preview.short_description = _("Prévisualisation")

    def approve_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _("%d témoignage(s) approuvé(s).") % updated)
    approve_testimonials.short_description = _("Approuver les témoignages sélectionnés")

    def disapprove_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _("%d témoignage(s) désapprouvé(s).") % updated)
    disapprove_testimonials.short_description = _("Désapprouver les témoignages sélectionnés")

# ---------------- Newsletter Subscriber Admin ----------------
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "subscribed_at", "is_active", "display_subscription_source"]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["email"]
    actions = ["activate_subscribers", "deactivate_subscribers"]
    readonly_fields = ["subscribed_at"]
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('email', 'is_active')
        }),
        (_('Subscription Info'), {
            'fields': ('subscribed_at',),
            'classes': ('collapse',)
        }),
    )

    def display_subscription_source(self, obj):
        contact_message = ContactMessage.objects.filter(email=obj.email, newsletter=True).first()
        return _("Via formulaire de contact") if contact_message else _("Via formulaire de newsletter")
    display_subscription_source.short_description = _("Source de l'inscription")

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("%d abonné(s) activé(s).") % updated)
    activate_subscribers.short_description = _("Activer les abonnés sélectionnés")

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("%d abonné(s) désactivé(s).") % updated)
    deactivate_subscribers.short_description = _("Désactiver les abonnés sélectionnés")

# ---------------- Contact Message Admin ----------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["nom", "email", "sujet", "created_at", "is_read", "newsletter"]
    list_filter = ["newsletter", "is_read", "created_at"]
    search_fields = ["nom", "email", "sujet", "message"]
    actions = ["mark_as_read", "mark_as_unread"]
    readonly_fields = ["created_at"]
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'email', 'phone', 'level', 'sujet', 'message')
        }),
        (_('Preferences'), {
            'fields': ('newsletter',)
        }),
        (_('Status'), {
            'fields': ('is_read',)
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def is_read(self, obj):
        return obj.is_read
    is_read.boolean = True
    is_read.short_description = _("Lu")

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, _("%d message(s) marqué(s) comme lu(s).") % updated)
    mark_as_read.short_description = _("Marquer comme lu")

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, _("%d message(s) marqué(s) comme non lu(s).") % updated)
    mark_as_unread.short_description = _("Marquer comme non lu")

# ---------------- Stat Value Admin ----------------
@admin.register(StatValue)
class StatValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'display_icon')
    list_editable = ('value',)
    search_fields = ('name',)
    
    def display_icon(self, obj):
        icons = {
            'students': '👨‍🎓',
            'teachers': '👨‍🏫',
            'success_rate': '📈',
            'years': '📅'
        }
        return icons.get(obj.name.lower(), '📊')
    display_icon.short_description = _('Icône')

# ---------------- Academic Event Admin ----------------
@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ("date", "activity", "responsible")
    search_fields = ("activity", "responsible")
    list_filter = ("date",)

# ---------------- Success Rate Admin ----------------
@admin.register(SuccessRate)
class SuccessRateAdmin(admin.ModelAdmin):
    list_display = ('year', 'rate', 'created_at')
    list_filter = ('year',)
    search_fields = ('year',)
    ordering = ('-year',)
    readonly_fields = ('created_at',)

# ---------------- Absence Admin ----------------
@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'reason']
    list_filter = ['date', 'teacher']
    search_fields = ['teacher__username', 'reason']
    ordering = ['date']

# ---------------- Reservation Admin ----------------
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'student_name', 'date']
    list_filter = ['date']
    search_fields = ['course_name', 'student_name']
    ordering = ['date']