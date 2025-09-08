# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Home / Dashboard ---
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # --- Posts ---
    path("poste/", views.post_view, name="post"),
    path("add_item/", views.post_add, name="add_item"),
    path("item/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("item/<int:pk>/delete/", views.delete_post, name="delete_post"),

    # --- Static / Pages ---
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("services/", views.services, name="services"),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),

    # --- Testimonials ---
    path("testimonials/", views.testimonials, name="testimonials"),
    path("testimonials/<int:pk>/detail/", views.testimonial_detail, name="testimonial_detail"),

    # --- Academic Events ---
    path("events/", views.events_list, name="events_list"),
    path("events/add/", views.event_add, name="event_add"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),

    # --- Calendrier Académique ---
    path("calendrier-academique/pdf/", views.calendrier_academique_pdf, name="calendrier_academique_pdf"),
    path("calendrier-academique/docx/", views.calendrier_academique_docx, name="calendrier_academique_docx"),
    path("calendrier-academique/generate/", views.generate_calendar, name="generate_calendar"),

    # --- Secrétariat ---
    path("secretary/", views.secretary_dashboard, name="secretary_dashboard"),
    path("secretary/report/pdf/", views.secretary_report_pdf, name="secretary_report_pdf"),
]
