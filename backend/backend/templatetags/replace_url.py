from django import template
register = template.Library()
def change_url(value, arg):
    return value.replace('/app/frontend/', '/static/')

register.filter("change_url", change_url)