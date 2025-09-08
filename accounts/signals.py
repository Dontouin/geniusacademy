from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    generate_admin_credentials,
    send_new_account_email,
)


def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Signal pour créer automatiquement les identifiants et envoyer l'email lors de la création d'un compte.
    Gère : étudiants, enseignants et admins.
    """
    if not created or instance is None:
        return

    # --- Étudiants ---
    if instance.is_student:
        username, password = generate_student_credentials()
        instance.username = username
        instance.set_password(password)
        instance.save(update_fields=["username", "password"])
        send_new_account_email(instance, password)

    # --- Enseignants ---
    elif instance.is_lecturer:
        username, password = generate_lecturer_credentials()
        instance.username = username
        instance.set_password(password)
        instance.save(update_fields=["username", "password"])
        send_new_account_email(instance, password)

    # --- Admins ---
    elif instance.is_superuser or getattr(instance, "is_admin", False):
        username, password = generate_admin_credentials()
        instance.username = username
        instance.set_password(password)
        instance.save(update_fields=["username", "password"])
        send_new_account_email(instance, password)
