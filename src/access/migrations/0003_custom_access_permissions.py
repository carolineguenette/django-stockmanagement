# **************************
# Dans app django access
# **************************

from django.db import migrations

# ===================================
# ACCESS
# ===================================
PERMISSIONS = [
    {
        "codename": "access.role.manage",
        "name": {
            "fr": "Gérer les rôles",
            "en": "Manage roles"
        },
        "help_text": {
            "fr": "Gérer les rôles et leur association avec des permissions. Cette permission est strictement encadrée pour empêcher l'escalade de privilèges.",
            "en": "Manage roles and their association with permissions. This permission is strictly controlled to prevent privilege escalation."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "DELEGATE",
        "display_order": 1,
    },
]

# ===================================
# USERS
# ===================================
PERMISSIONS += [
    {
        "codename": "users.user.add",
        "name": {
            "fr": "Créer un utilisateur",
            "en": "Create user"
        },
        "help_text": {
            "fr": "Créer un nouvel utilisateur dans le système. L'utilisateur créé sera un subordonné de l'utilisateur créateur.",
            "en": "Create a new user in the system. The created user will be a subordinate of the creator user."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 50,
    },
    {
        "codename": "users.user.invite",
        "name": {
            "fr": "Inviter un utilisateur",
            "en": "Invite user"
        },
        "help_text": {
            "fr": "Inviter un utilisateur à créer son propre compte à partir d'un courriel contenant un lien sécurisé.",
            "en": "Invite a user to create their own account via an email containing a secure link."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 51,
    },
    {
        "codename": "users.user.view",
        "name": {
            "fr": "Voir les utilisateurs",
            "en": "View users"
        },
        "help_text": {
            "fr": "Voir la liste des utilisateurs, incluant leur secteur d'activité. Un utilisateur avec cette permission ne voit que ses subordonnés.",
            "en": "View the user list, including their line of business. A user with this permission only sees their subordinates."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 52,
    },
    {
        "codename": "users.user.change",
        "name": {
            "fr": "Modifier un utilisateur",
            "en": "Modify user"
        },
        "help_text": {
            "fr": "Modifier les informations ou préférences d'un utilisateur, excluant le drapeau propriétaire. Un utilisateur avec cette permission ne peut modifier que ses subordonnés.",
            "en": "Modify a user's information or preferences, excluding the owner flag. A user with this permission can only modify their subordinates."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 53,
    },
    {
        "codename": "users.user.change_own",
        "name": {
            "fr": "Modifier son propre profil",
            "en": "Modify own profile"
        },
        "help_text": {
            "fr": "Modifier les informations et préférences de son propre profil. Exclut la modification du statut propriétaire et du superviseur.",
            "en": "Modify information and preferences of one's own profile. Excludes modifying the owner status and supervisor."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 54,
    },
    {
        "codename": "users.user.delete",
        "name": {
            "fr": "Supprimer un utilisateur",
            "en": "Delete user"
        },
        "help_text": {
            "fr": "Supprimer un utilisateur. Le système refusera s'il existe des références à cet utilisateur ou s'il est propriétaire.",
            "en": "Delete a user. The system will refuse if references to this user exist or if they are an owner."
        },
        "context": "SYSTEM",
        "sensibility": "MEDIUM",
        "category": "USERS",
        "display_order": 55,
    },
    {
        "codename": "users.user.setactivation",
        "name": {
            "fr": "Activer/désactiver un compte",
            "en": "Activate/deactivate account"
        },
        "help_text": {
            "fr": "Activer ou désactiver le compte d'un utilisateur. Un utilisateur avec cette permission ne peut changer le statut que de ses subordonnés.",
            "en": "Activate or deactivate a user's account. A user with this permission can only change the status of their subordinates."
        },
        "context": "SYSTEM",
        "sensibility": "LOW",
        "category": "USERS",
        "display_order": 56,
    },
    {
        "codename": "users.userrole.view",
        "name": {
            "fr": "Voir les rôles assignés",
            "en": "View assigned roles"
        },
        "help_text": {
            "fr": "Consulter les rôles assignés à une liste d'utilisateurs. Un utilisateur avec cette permission ne peut voir les permissions que de ses subordonnés.",
            "en": "Consult roles assigned to a list of users. A user with this permission can only see the permissions of their subordinates."
        },
        "context": "SYSTEM",
        "sensibility": "MEDIUM",
        "category": "USERS",
        "display_order": 57,
    },
    {
        "codename": "users.userrole.manage",
        "name": {
            "fr": "Gérer les rôles assignés",
            "en": "Manage assigned roles"
        },
        "help_text": {
            "fr": "Assigner, modifier ou supprimer les rôles assignés à un utilisateur. Strictement limité aux subordonnés et aux permissions détenues.",
            "en": "Assign, modify, or remove roles assigned to a user. Strictly limited to subordinates and held permissions."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "DELEGATE",
        "display_order": 58,
    },
    {
        "codename": "users.userrolelog.view",
        "name": {
            "fr": "Voir l'historique des rôles",
            "en": "View role history"
        },
        "help_text": {
            "fr": "Voir l'historique des modifications sur les assignations de rôle. Un utilisateur avec cette permission ne voit les informations que de ses subordonnés.",
            "en": "View modification history on role assignments. A user with this permission only sees information of their subordinates."
        },
        "context": "SYSTEM",
        "sensibility": "MEDIUM",
        "category": "USERS",
        "display_order": 59,
    },
]

# ===================================
# COMPANY
# ===================================
PERMISSIONS += [
    {
        "codename": "company.company.view",
        "name": {
            "fr": "Voir les informations de l'entreprise",
            "en": "View company information"
        },
        "help_text": {
            "fr": "Voir les informations de configuration de l'entreprise.",
            "en": "View company configuration information."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "COMPANY",
        "display_order": 100,
    },
    {
        "codename": "company.locationtype.manage",
        "name": {
            "fr": "Gérer les types de location",
            "en": "Manage location types"
        },
        "help_text": {
            "fr": "Gérer les types de location (voir, ajouter, modifier et supprimer).",
            "en": "Manage location types (view, add, modify, and delete)."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "COMPANY",
        "display_order": 101,
    },
    {
        "codename": "company.location.view",
        "name": {
            "fr": "Consulter les emplacements",
            "en": "Consult locations"
        },
        "help_text": {
            "fr": "Consulter les emplacements de l'entreprise.",
            "en": "Consult company locations."
        },
        "context": "COMPANY",
        "sensibility": "LOW",
        "category": "COMPANY",
        "display_order": 102,
    },
    {
        "codename": "company.location.sub.manage",
        "name": {
            "fr": "Gérer les sous-locations",
            "en": "Manage sub-locations"
        },
        "help_text": {
            "fr": "Gérer les sous-locations (emplacements enfants). Le système vérifie que le parent appartient à la même entreprise.",
            "en": "Manage sub-locations (child locations). The system checks that the parent belongs to the same company."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "COMPANY",
        "display_order": 103,
    },
    {
        "codename": "company.uom.view",
        "name": {
            "fr": "Consulter les unités de mesure",
            "en": "Consult units of measure"
        },
        "help_text": {
            "fr": "Consulter toutes les unités de mesure définies dans l'entreprise.",
            "en": "Consult all units of measure defined in the company."
        },
        "context": "COMPANY",
        "sensibility": "LOW",
        "category": "COMPANY",
        "display_order": 104,
    },
    {
        "codename": "company.uom.manage",
        "name": {
            "fr": "Gérer les unités de mesure",
            "en": "Manage units of measure"
        },
        "help_text": {
            "fr": "Gérer toutes les unités de mesure utilisées dans l'entreprise.",
            "en": "Manage all units of measure used in the company."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "COMPANY",
        "display_order": 105,
    },
]

# ===================================
# CATALOGUE
# ===================================
PERMISSIONS += [
    {
        "codename": "catalogue.product.view",
        "name": {
            "fr": "Consulter le catalogue",
            "en": "Consult catalogue"
        },
        "help_text": {
            "fr": "Consulter le catalogue des produits (inclut les modèles, variantes, catégories, images et conditionnement).",
            "en": "Consult the product catalogue (includes models, variants, categories, images, and packaging)."
        },
        "context": "COMPANY",
        "sensibility": "LOW",
        "category": "CATALOGUE",
        "display_order": 150,
    },
    {
        "codename": "catalogue.product.add",
        "name": {
            "fr": "Créer un produit",
            "en": "Create product"
        },
        "help_text": {
            "fr": "Créer un nouveau produit (inclut les modèles, variantes, catégories, images et conditionnement).",
            "en": "Create a new product (includes models, variants, categories, images, and packaging)."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "CATALOGUE",
        "display_order": 151,
    },
    {
        "codename": "catalogue.product.change",
        "name": {
            "fr": "Modifier un produit",
            "en": "Modify product"
        },
        "help_text": {
            "fr": "Modifier les caractéristiques d'une fiche produit (inclut les modèles, variantes, catégories, images et conditionnement).",
            "en": "Modify the features of a product file (includes models, variants, categories, images, and packaging)."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "CATALOGUE",
        "display_order": 152,
    },
    {
        "codename": "catalogue.product.imagesupload",
        "name": {
            "fr": "Téléverser des images de produit",
            "en": "Upload product images"
        },
        "help_text": {
            "fr": "Téléverser des images sur le serveur en lien avec le produit. Nécessite la permission de modifier un produit.",
            "en": "Upload images to the server related to the product. Requires permission to modify a product."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "CATALOGUE",
        "display_order": 153,
    },
    {
        "codename": "catalogue.product.archive",
        "name": {
            "fr": "Archiver un produit",
            "en": "Archive product"
        },
        "help_text": {
            "fr": "Archiver ou désarchiver un produit. Un produit archivé n'apparaît plus dans les listes ni les recherches.",
            "en": "Archive or unarchive a product. An archived product no longer appears in lists or searches."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "CATALOGUE",
        "display_order": 154,
    },
    {
        "codename": "catalogue.product.delete",
        "name": {
            "fr": "Supprimer un produit",
            "en": "Delete product"
        },
        "help_text": {
            "fr": "Supprimer définitivement un produit du catalogue. Le système bloquera la suppression si des références existent.",
            "en": "Permanently delete a product from the catalogue. The system will block deletion if references exist."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "CATALOGUE",
        "display_order": 155,
    },
    {
        "codename": "catalogue.category.view",
        "name": {
            "fr": "Consulter les catégories",
            "en": "Consult categories"
        },
        "help_text": {
            "fr": "Consulter l'arborescence complète des catégories.",
            "en": "Consult the full category tree."
        },
        "context": "COMPANY",
        "sensibility": "LOW",
        "category": "CATALOGUE",
        "display_order": 156,
    },
    {
        "codename": "catalogue.category.manage",
        "name": {
            "fr": "Gérer les catégories",
            "en": "Manage categories"
        },
        "help_text": {
            "fr": "Gérer les catégories. Le système bloquera la suppression d'une catégorie référencée.",
            "en": "Manage categories. The system will block the deletion of a referenced category."
        },
        "context": "COMPANY",
        "sensibility": "MEDIUM",
        "category": "CATALOGUE",
        "display_order": 157,
    },
    {
        "codename": "catalogue.attribute.manage",
        "name": {
            "fr": "Gérer les attributs de variantes",
            "en": "Manage variant attributes"
        },
        "help_text": {
            "fr": "Gérer les attributs (clé et valeurs) de variantes de produit dans un module dédié.",
            "en": "Manage attributes (key and values) of product variants in a dedicated module."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "CATALOGUE",
        "display_order": 158,
    },
]

# ===================================
# INVENTORY
# ===================================
PERMISSIONS += [
    {
        "codename": "inventory.stock.view",
        "name": {
            "fr": "Consulter les stocks",
            "en": "Consult stocks"
        },
        "help_text": {
            "fr": "Consulter les quantités de stock disponibles.",
            "en": "Consult available stock quantities."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "INVENTORY",
        "display_order": 200,
    },
    {
        "codename": "inventory.movement.view",
        "name": {
            "fr": "Consulter les mouvements de stock",
            "en": "Consult stock movements"
        },
        "help_text": {
            "fr": "Consulter le journal historique des mouvements de stock. Permet de rechercher et filtrer.",
            "en": "Consult the historical log of stock movements. Allows searching and filtering."
        },
        "context": "COMPANY",
        "sensibility": "LOW",
        "category": "INVENTORY",
        "display_order": 201,
    },
    {
        "codename": "inventory.movementreason.manage",
        "name": {
            "fr": "Gérer les raisons de mouvement",
            "en": "Manage movement reasons"
        },
        "help_text": {
            "fr": "Gérer les raisons pour modifier les quantités en inventaire. Permet d'associer la permission requise à la raison.",
            "en": "Manage reasons for modifying inventory quantities. Allows associating the required permission with the reason."
        },
        "context": "COMPANY",
        "sensibility": "HIGH",
        "category": "INVENTORY",
        "display_order": 202,
    },
    {
        "codename": "inventory.stock.increase",
        "name": {
            "fr": "Augmenter l'inventaire",
            "en": "Increase inventory"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire (permission générique).",
            "en": "Increase inventory (generic permission)."
        },
        "context": "LOCATION",
        "sensibility": "HIGH",
        "category": "MOVEMENT",
        "display_order": 203,
    },
    {
        "codename": "inventory.stock.decrease",
        "name": {
            "fr": "Diminuer l'inventaire",
            "en": "Decrease inventory"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire (permission générique).",
            "en": "Decrease inventory (generic permission)."
        },
        "context": "LOCATION",
        "sensibility": "HIGH",
        "category": "MOVEMENT",
        "display_order": 204,
    },
    {
        "codename": "inventory.stock.purchase",
        "name": {
            "fr": "Réception achat fournisseur",
            "en": "Supplier purchase reception"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en raison d'une commande d'achat à un fournisseur.",
            "en": "Increase inventory due to a purchase order from a supplier."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 205,
    },
    {
        "codename": "inventory.stock.manufacture",
        "name": {
            "fr": "Réception production interne",
            "en": "Internal production reception"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en raison de l'arrivée de produits issus d'une chaîne de production interne.",
            "en": "Increase inventory due to the arrival of products from an internal production line."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 206,
    },
    {
        "codename": "inventory.stock.sale",
        "name": {
            "fr": "Vente",
            "en": "Sale"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire en raison d'une vente.",
            "en": "Decrease inventory due to a sale."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 207,
    },
    {
        "codename": "inventory.stock.count_more",
        "name": {
            "fr": "Ajustement inventaire (plus)",
            "en": "Inventory adjustment (plus)"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en raison d'un ajustement de décompte d'inventaire.",
            "en": "Increase inventory due to a stock count adjustment."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 208,
    },
    {
        "codename": "inventory.stock.count_less",
        "name": {
            "fr": "Ajustement inventaire (moins)",
            "en": "Inventory adjustment (minus)"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire en raison d'un ajustement de décompte d'inventaire.",
            "en": "Decrease inventory due to a stock count adjustment."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 209,
    },
    {
        "codename": "inventory.stock.loss",
        "name": {
            "fr": "Perte de marchandise",
            "en": "Goods loss"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire en raison de marchandises perdues (bris, vol, date de péremption dépassée, etc.).",
            "en": "Decrease inventory due to lost goods (breakage, theft, expired date, etc.)."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 210,
    },
    {
        "codename": "inventory.stock.uom_pack",
        "name": {
            "fr": "Changement d'unité de mesure (emballage)",
            "en": "Unit of mesure change (pack)"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire en raison d'un changement d'unité de mesure (unité vers pack).",
            "en": "Decrease inventory due to a unit of measure change (unit to pack)."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 211,
    },
    {
        "codename": "inventory.stock.uom_unpack",
        "name": {
            "fr": "Changement d'unité de mesure (déballage)",
            "en": "Unit of measure change (unpack)"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en raison d'un changement d'unité de mesure (pack vers unité).",
            "en": "Increase inventory due to a unit of measure change (pack to unit)."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 212,
    },
    {
        "codename": "inventory.stock.relocate",
        "name": {
            "fr": "Relocaliser dans même emplacement",
            "en": "Relocate within same location"
        },
        "help_text": {
            "fr": "Relocaliser le stock dans un emplacement ayant le même parent principal.",
            "en": "Relocate stock to a location sharing the same main parent."
        },
        "context": "MULTI_LOCATIONS",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 213,
    },
    {
        "codename": "inventory.stock.transfer_out",
        "name": {
            "fr": "Transfert sortant",
            "en": "Outgoing transfer"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent.",
            "en": "Decrease inventory to send it to a location with a different main parent."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 214,
    },
    {
        "codename": "inventory.stock.transfer_in",
        "name": {
            "fr": "Transfert entrant",
            "en": "Incoming transfer"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en réceptionnant un transfert entrant.",
            "en": "Increase inventory by receiving an incoming transfer."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 215,
    },
    {
        "codename": "inventory.stock.intercompany_out",
        "name": {
            "fr": "Transfert inter-compagnie sortant",
            "en": "Outgoing intercompany transfer"
        },
        "help_text": {
            "fr": "Diminuer l'inventaire en raison d'une vente interne vers une entreprise du même propriétaire.",
            "en": "Decrease inventory due to an internal sale to a company under the same owner."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 216,
    },
    {
        "codename": "inventory.stock.intercompany_in",
        "name": {
            "fr": "Transfert inter-compagnie entrant",
            "en": "Incoming intercompany transfer"
        },
        "help_text": {
            "fr": "Augmenter l'inventaire en raison de la réception interne de stock d'une entreprise du même propriétaire.",
            "en": "Increase inventory due to the internal reception of stock from a company under the same owner."
        },
        "context": "LOCATION",
        "sensibility": "MEDIUM",
        "category": "MOVEMENT",
        "display_order": 217,
    },
]

# ===================================
# REPORTING
# ===================================
PERMISSIONS += [
    {
        "codename": "reporting.view",
        "name": {
            "fr": "Voir les rapports consolidés",
            "en": "View consolidated reports"
        },
        "help_text": {
            "fr": "Lecture des rapports rassemblant les données de plusieurs entreprises.",
            "en": "Read reports gathering data from multiple companies."
        },
        "context": "MULTI_COMPANIES",
        "sensibility": "HIGH",
        "category": "REPORTING",
        "display_order": 300,
    },
    {
        "codename": "reporting.stock_levels.view",
        "name": {
            "fr": "Voir les rapports de stock",
            "en": "View stock reports"
        },
        "help_text": {
            "fr": "Lecture des rapports de rotations, ruptures imminentes et seuils d'alerte.",
            "en": "Read stock rotation, imminent shortage, and alert threshold reports."
        },
        "context": "MULTI_COMPANIES",
        "sensibility": "HIGH",
        "category": "REPORTING",
        "display_order": 301,
    },
]

# ==============================================
# Opérations ORM et Classe de Migration
# ==============================================
def create_permissions(apps, schema_editor):
    """
    Crée les permissions globales et leurs enregistrements de traduction
    en itérant dynamiquement sur la structure de dictionnaire imbriquée.
    """
    Permission = apps.get_model("access", "Permission")
    PermissionTranslation = apps.get_model("access", "PermissionTranslation")

    for perm_data in PERMISSIONS:
        # 1. Isolation des dictionnaires de traduction imbriqués
        name_translations = perm_data.pop("name")
        help_text_translations = perm_data.pop("help_text")

        # 2. Création de l'objet de base dans la table principale (ex: access_permission)
        permission_obj, created = Permission.objects.get_or_create(
            codename=perm_data["codename"],
            defaults=perm_data
        )

        # 3. Extraction dynamique de toutes les langues disponibles (fr, en, etc.)
        languages = set(name_translations.keys()).union(help_text_translations.keys())

        # 4. Écriture / Alignement des lignes dans la table Parler (ex: access_permission_translation)
        for lang_code in languages:
            PermissionTranslation.objects.get_or_create(
                master=permission_obj,
                language_code=lang_code,
                defaults={
                    "name": name_translations.get(lang_code, ""),
                    "help_text": help_text_translations.get(lang_code, ""),
                }
            )


class Migration(migrations.Migration):
    dependencies = [
        ("access", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_permissions),
    ]

