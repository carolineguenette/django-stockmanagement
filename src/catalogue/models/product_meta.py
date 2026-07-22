# # Étape 2 (Plus tard dans le projet selon...)
# # BUT: Permettre de traduire les infos Product
#
# class ProductMeta(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="metas")
#     language = models.CharField(max_length=10, db_index=True) # 'en-ca', 'fr-ca', etc.
#     key = models.CharField(max_length=50) # 'name', 'description'
#     value = models.TextField()
#
#     class Meta:
#         unique_together = ('product', 'language', 'key')

# ET ajout d'une @property dans model Product pour aller cherche la traduction dans ProductMeta
# ou se rabattre sur name si absente
