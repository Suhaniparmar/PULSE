from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def qs_with(context, **kwargs):
    """Current query string with the given keys replaced (empty value removes the key); page is reset."""
    params = context["request"].GET.copy()
    params.pop("page", None)
    for key, value in kwargs.items():
        if value in ("", None):
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"


@register.filter
def abs_val(value):
    try:
        return abs(value)
    except TypeError:
        return value
