from django import template

register = template.Library()

@register.filter
def contem(valor, pesquisa):
    return pesquisa in valor
