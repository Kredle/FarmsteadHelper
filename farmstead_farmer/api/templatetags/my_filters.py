from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    return value.split(delimiter)

@register.filter
def filter_by_category(items, category):
    """Фільтр для вибору елементів тільки з певною категорією."""
    return [item for item in items if item.get('category') == category]