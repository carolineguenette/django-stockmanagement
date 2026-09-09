# **************************
# Dans app django company
# **************************

from django.db import migrations

COUNTRIES = [
    {"iso_code": "AF", "name": {"fr": "Afghanistan", "en": "Afghanistan"}},
    {"iso_code": "ZA", "name": {"fr": "Afrique du Sud", "en": "South Africa"}},
    {"iso_code": "AL", "name": {"fr": "Albanie", "en": "Albania"}},
    {"iso_code": "DZ", "name": {"fr": "Algérie", "en": "Algeria"}},
    {"iso_code": "DE", "name": {"fr": "Allemagne", "en": "Germany"}},
    {"iso_code": "SA", "name": {"fr": "Arabie saoudite", "en": "Saudi Arabia"}},
    {"iso_code": "AR", "name": {"fr": "Argentine", "en": "Argentina"}},
    {"iso_code": "AU", "name": {"fr": "Australie", "en": "Australia"}},
    {"iso_code": "AT", "name": {"fr": "Autriche", "en": "Austria"}},
    {"iso_code": "BE", "name": {"fr": "Belgique", "en": "Belgium"}},
    {"iso_code": "BR", "name": {"fr": "Brésil", "en": "Brazil"}},
    {"iso_code": "CA", "name": {"fr": "Canada", "en": "Canada"}},
    {"iso_code": "CL", "name": {"fr": "Chili", "en": "Chile"}},
    {"iso_code": "CN", "name": {"fr": "Chine", "en": "China"}},
    {"iso_code": "CY", "name": {"fr": "Chypre", "en": "Cyprus"}},
    {"iso_code": "CO", "name": {"fr": "Colombie", "en": "Colombia"}},
    {"iso_code": "KR", "name": {"fr": "Corée du Sud", "en": "South Korea"}},
    {"iso_code": "HR", "name": {"fr": "Croatie", "en": "Croatia"}},
    {"iso_code": "DK", "name": {"fr": "Danemark", "en": "Denmark"}},
    {"iso_code": "EG", "name": {"fr": "Égypte", "en": "Egypt"}},
    {"iso_code": "AE", "name": {"fr": "Émirats arabes unis", "en": "United Arab Emirates"}},
    {"iso_code": "ES", "name": {"fr": "Espagne", "en": "Spain"}},
    {"iso_code": "EE", "name": {"fr": "Estonie", "en": "Estonia"}},
    {"iso_code": "US", "name": {"fr": "États-Unis", "en": "United States"}},
    {"iso_code": "FI", "name": {"fr": "Finlande", "en": "Finland"}},
    {"iso_code": "FR", "name": {"fr": "France", "en": "France"}},
    {"iso_code": "GR", "name": {"fr": "Grèce", "en": "Greece"}},
    {"iso_code": "HU", "name": {"fr": "Hongrie", "en": "Hungary"}},
    {"iso_code": "IN", "name": {"fr": "Inde", "en": "India"}},
    {"iso_code": "ID", "name": {"fr": "Indonésie", "en": "Indonesia"}},
    {"iso_code": "IE", "name": {"fr": "Irlande", "en": "Ireland"}},
    {"iso_code": "IS", "name": {"fr": "Islande", "en": "Iceland"}},
    {"iso_code": "IL", "name": {"fr": "Israël", "en": "Israel"}},
    {"iso_code": "IT", "name": {"fr": "Italie", "en": "Italy"}},
    {"iso_code": "JP", "name": {"fr": "Japon", "en": "Japan"}},
    {"iso_code": "LU", "name": {"fr": "Luxembourg", "en": "Luxembourg"}},
    {"iso_code": "MA", "name": {"fr": "Maroc", "en": "Morocco"}},
    {"iso_code": "MX", "name": {"fr": "Mexique", "en": "Mexico"}},
    {"iso_code": "NO", "name": {"fr": "Norvège", "en": "Norway"}},
    {"iso_code": "NZ", "name": {"fr": "Nouvelle-Zélande", "en": "New Zealand"}},
    {"iso_code": "NL", "name": {"fr": "Pays-Bas", "en": "Netherlands"}},
    {"iso_code": "PL", "name": {"fr": "Pologne", "en": "Poland"}},
    {"iso_code": "PT", "name": {"fr": "Portugal", "en": "Portugal"}},
    {"iso_code": "QA", "name": {"fr": "Qatar", "en": "Qatar"}},
    {"iso_code": "RO", "name": {"fr": "Roumanie", "en": "Romania"}},
    {"iso_code": "GB", "name": {"fr": "Royaume-Uni", "en": "United Kingdom"}},
    {"iso_code": "RU", "name": {"fr": "Russie", "en": "Russia"}},
    {"iso_code": "SG", "name": {"fr": "Singapour", "en": "Singapore"}},
    {"iso_code": "SE", "name": {"fr": "Suède", "en": "Sweden"}},
    {"iso_code": "CH", "name": {"fr": "Suisse", "en": "Switzerland"}},
    {"iso_code": "TR", "name": {"fr": "Turquie", "en": "Turkey"}},
    {"iso_code": "UA", "name": {"fr": "Ukraine", "en": "Ukraine"}},
    {"iso_code": "VN", "name": {"fr": "Viêt Nam", "en": "Vietnam"}},
]



def populate_countries(apps, schema_editor):
    # Récupération des modèles historiques
    CompanyCountry = apps.get_model('company', 'Country')
    CompanyCountryTranslation = apps.get_model('company', 'CountryTranslation')

    for country_data in COUNTRIES:
        # 1. Création de l'entrée principale avec le code ISO
        country_instance = CompanyCountry.objects.create(
            iso_code=country_data["iso_code"]
        )

        # 2. Création de chaque traduction associée dans la table générée par Parler
        for lang, localized_name in country_data["name"].items():
            CompanyCountryTranslation.objects.create(
                master=country_instance,
                language_code=lang,
                name=localized_name
            )

class Migration(migrations.Migration):
    dependencies = [
        # Indiquez ici le nom exact de votre migration précédente
        ('company', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(populate_countries),
    ]
