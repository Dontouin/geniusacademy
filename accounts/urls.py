from django.urls import path, include
from .views import (
    admin_panel,
    profile,
    profile_single,
    profile_update,
    change_password,
    LecturerFilterView,
    StudentFilterView,
    OtherFilterView,
    ParentFilterView,  # AJOUT: Import de la vue pour les parents
    staff_add_view,
    edit_staff,
    delete_staff,
    student_add_view,
    edit_student,
    delete_student,
    other_add_view,
    edit_other,
    delete_other,
    other_list,
    ParentAdd,
    edit_parent,  # AJOUT: Vues pour parents
    delete_parent,
    parent_list,  # AJOUT: Liste des parents
    validate_username,
    register_choice,
    register_user,
    teacher_info_add,
    teacher_info_edit,
    teacher_info_delete,
    render_lecturer_pdf_list,
    render_student_pdf_list,
    render_other_pdf_list,
    render_parent_pdf_list,  # AJOUT: Export PDF pour parents
    teacher_info_pdf,
    user_login,
    user_logout,
)

urlpatterns = [
    # Auth routes
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("", include("django.contrib.auth.urls")),  # routes par défaut: password_reset, etc.

     # Admin Panel
    path("admin_panel/", admin_panel, name="admin_panel"),

    # Dashboard & profile
    path("profile/", profile, name="profile"),
    path("profile/<int:user_id>/detail/", profile_single, name="profile_single"),
    path("setting/", profile_update, name="edit_profile"),
    path("change_password/", change_password, name="change_password"),

    # Lecturers
    path("lecturers/", LecturerFilterView.as_view(), name="lecturer_list"),
    path("lecturer/add/", staff_add_view, name="add_lecturer"),
    path("staff/<int:pk>/edit/", edit_staff, name="staff_edit"),
    path("lecturers/<int:pk>/delete/", delete_staff, name="lecturer_delete"),

    # Students
    path("students/", StudentFilterView.as_view(), name="student_list"),
    path("student/add/", student_add_view, name="add_student"),
    path("student/<int:pk>/edit/", edit_student, name="student_edit"),
    path("students/<int:pk>/delete/", delete_student, name="student_delete"),
    
    # Parents
    path("parents/", ParentFilterView.as_view(), name="parent_list"),  # AJOUT: Liste des parents
    path("parents/add/", ParentAdd.as_view(), name="add_parent"),
    path("parent/<int:pk>/edit/", edit_parent, name="edit_parent"),  # AJOUT: Édition parent
    path("parent/<int:pk>/delete/", delete_parent, name="delete_parent"),  # AJOUT: Suppression parent

    # # Autres utilisateurs
    # path("others/", OtherFilterView.as_view(), name="other_list"),
    # path("other/add/", other_add_view, name="other_add"),
    # path("other/<int:pk>/edit/", edit_other, name="edit_other"),
    # path("other/<int:pk>/delete/", delete_other, name="delete_other"),

    # AJAX
    path("ajax/validate-username/", validate_username, name="validate_username"),

    # Registration multi-type
    path("register/", register_choice, name="register_choice"),
    path("register/<str:user_type>/", register_user, name="register_user"),

    # Teacher Info / Fiche
    path("teacher_info/add/", teacher_info_add, name="teacher_info_add"),
    path("teacher_info/pdf/<int:pk>/", teacher_info_pdf, name="teacher_info_pdf"),
    path("teacher_info/<int:pk>/edit/", teacher_info_edit, name="teacher_info_edit"),
    path("teacher_info/<int:pk>/delete/", teacher_info_delete, name="teacher_info_delete"),

    # PDF exports
    path("create_lecturers_pdf_list/", render_lecturer_pdf_list, name="lecturer_list_pdf"),
    path("create_students_pdf_list/", render_student_pdf_list, name="student_list_pdf"),
    path("create_others_pdf_list/", render_other_pdf_list, name="other_list_pdf"),
    path("create_parents_pdf_list/", render_parent_pdf_list, name="parent_list_pdf"),  # AJOUT: Export PDF parents
]