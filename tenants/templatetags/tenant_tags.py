from django import template

register = template.Library()


@register.filter
def has_module(tenant, module_name):
    """
    Usage in templates:
        {% load tenant_tags %}
        {% if request.tenant|has_module:"payroll" %}
            <a href="/payroll/">Payroll</a>
        {% endif %}
    """
    if tenant is None:
        return True  # non-tenant context (e.g. superadmin) — show everything
    return tenant.module_enabled(module_name)