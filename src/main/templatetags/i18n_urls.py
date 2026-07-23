from django import template
from django.urls import translate_url

register = template.Library()

@register.simple_tag(takes_context=True)
def custom_translate_url(context, lang_code):
    request = context.get('request')
    if request:
        # Utilise la fonction Python native de Django pour traduire l'URL relative courante
        return translate_url(request.get_full_path(), lang_code)
    return ''
