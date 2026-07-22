# src/catalogue/admin.py
from django.contrib import admin
from .models.product import Product
from .models.product_image import ProductImage

# Permet d'intégrer la gestion des images directement dans la page du produit
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Affiche par défaut 1 ligne vide prête à recevoir une image
    fields = ('image', 'alt_text', 'is_main')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('sku', 'name', 'price', 'alert_threshold', 'created_by', 'updated_at')
    search_fields = ('sku', 'name', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')

    # Injection des lignes d'images à l'intérieur du formulaire produit
    inlines = [ProductImageInline]

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('sku', 'name', 'description')
        }),
        ('Tarification & Alertes', {
            'fields': ('price', 'alert_threshold'),
        }),
        ('Audit & Traçabilité', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',), # Masque la section par défaut pour un look plus épuré
        }),
    )

    # Automatisation à la création
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.created_by = request.user
        obj.updated_by = request.user  # Toujours mis à jour à la modification
        super().save_model(request, obj, form, change)
