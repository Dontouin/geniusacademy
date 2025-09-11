from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging
from .utils import (
    generate_lecturer_credentials,
    send_new_account_email,
)
from .models import User

# Configuration du logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def handle_lecturer_credentials(sender, instance, created, **kwargs):
    """
    Gestion sécurisée des identifiants enseignants avec transaction
    et prévention des boucles.
    """
    # Vérifier si c'est un nouvel utilisateur ET un enseignant
    if not created or not instance.is_lecturer:
        return
    
    # Vérifier si déjà traité dans cette session
    if hasattr(instance, '_lecturer_credentials_processed'):
        return
    
    # Marquer comme traité immédiatement pour éviter les boucles
    instance._lecturer_credentials_processed = True
    
    with transaction.atomic():
        try:
            # Verrouiller l'enregistrement pour éviter les conflits
            user = User.objects.select_for_update().get(pk=instance.pk)
            
            # Vérifier si le username est déjà défini (ne commence pas par le préfixe)
            if user.username and not user.username.startswith('25TGA'):
                logger.info(f"Username déjà défini pour l'enseignant {user.pk}: {user.username}")
                return
                
            # Générer les identifiants
            username, password = generate_lecturer_credentials()
            
            # Mettre à jour l'utilisateur
            user.username = username
            user.password = make_password(password)
            user.save(update_fields=['username', 'password'])
            
            # Envoyer l'email (hors transaction)
            transaction.on_commit(
                lambda: send_new_account_email(user, password)
            )
            
            logger.info(f"Identifiants générés pour l'enseignant {user.pk}: {username}")
            
        except ObjectDoesNotExist:
            logger.error(f"Utilisateur {instance.pk} n'existe plus lors de la génération des identifiants")
        except Exception as e:
            logger.error(f"Erreur génération identifiants enseignant {instance.pk}: {e}")
            # En cas d'erreur, on retire le flag pour permettre une nouvelle tentative
            if hasattr(instance, '_lecturer_credentials_processed'):
                delattr(instance, '_lecturer_credentials_processed')