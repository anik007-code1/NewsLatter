from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Subscriber


class SubscriptionForm(forms.ModelForm):
    """Form for newsletter subscription"""
    
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name (optional)',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name (optional)',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Subscribe to Newsletter', css_class='btn btn-primary btn-lg')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists and is active
            existing_subscriber = Subscriber.objects.filter(email=email).first()
            if existing_subscriber and existing_subscriber.is_active and existing_subscriber.is_confirmed:
                raise forms.ValidationError("This email is already subscribed to our newsletter.")
            # If subscriber exists but is inactive or unconfirmed, we'll reactivate them in the view
        return email


class UnsubscribeForm(forms.Form):
    """Form for unsubscribing from newsletter"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Submit('submit', 'Unsubscribe', css_class='btn btn-danger')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                subscriber = Subscriber.objects.get(email=email, is_active=True)
            except Subscriber.DoesNotExist:
                raise forms.ValidationError("This email is not subscribed to our newsletter.")
        return email
