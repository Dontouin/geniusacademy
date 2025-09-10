from django.utils.translation import gettext_lazy as _

# -----------------------------
# Constantes et choix
# -----------------------------
PERE = _("Père")
MERE = _("Mère")
FRERE = _("Frère")
SOEUR = _("Sœur")
GRAND_MERE = _("Grand-mère")
GRAND_PERE = _("Grand-père")
AUTRE = _("Autre")

RELATION_SHIP = (
    (PERE, _("Père")),
    (MERE, _("Mère")),
    (FRERE, _("Frère")),
    (SOEUR, _("Sœur")),
    (GRAND_MERE, _("Grand-mère")),
    (GRAND_PERE, _("Grand-père")),
    (AUTRE, _("Autre")),
)

GENDERS = ((_("M"), _("Masculin")), (_("F"), _("Féminin")))

STATUT_MATRIMONIAL = (
    ("single", _("Célibataire")),
    ("married", _("Marié(e)")),
    ("divorced", _("Divorcé(e)")),
    ("widowed", _("Veuf(ve)")),
)