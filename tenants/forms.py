from django import forms

from tenants.models import AVAILABLE_MODULES, RechargeLog, Tenant

MODULE_CHOICES = AVAILABLE_MODULES


class TenantForm(forms.ModelForm):
    enabled_modules = forms.MultipleChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Which modules this customer will be able to use.",
    )

    class Meta:
        model = Tenant
        fields = [
            'name', 'subdomain', 'plan', 'employee_limit',
            'enabled_modules', 'contact_email', 'contact_phone',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Acme Pvt Ltd'}),
            'subdomain': forms.TextInput(attrs={'placeholder': 'acme'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'billing@acme.com'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Optional'}),
        }


class RechargeForm(forms.ModelForm):
    class Meta:
        model = RechargeLog
        fields = ['amount', 'days_added', 'payment_reference', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': '2999'}),
            'days_added': forms.NumberInput(attrs={'placeholder': '30'}),
            'payment_reference': forms.TextInput(attrs={'placeholder': 'Razorpay/UTR ref (optional)'}),
            'note': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }