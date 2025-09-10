from .utils import (
    generate_lecturer_credentials,
    send_new_account_email,
)


def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Signal pour créer automatiquement les identifiants et envoyer l'email.
    UNIQUEMENT pour les enseignants maintenant.
    """
    if not created or instance is None:
        return

    # --- Enseignants SEULEMENT ---
    if instance.is_lecturer:
        username, password = generate_lecturer_credentials()
        instance.username = username
        instance.set_password(password)
        instance.save(update_fields=["username", "password"])
        send_new_account_email(instance, password)

    # --- Pour tous les autres types (étudiants, parents, autres, admins) ---
    # NE RIEN FAIRE - ils doivent s'inscrire manuellement
    # avec leurs propres identifiants