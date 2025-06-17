from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Newsletter


class NewsletterForm(forms.ModelForm):
    """Form for creating and editing newsletters"""
    
    class Meta:
        model = Newsletter
        fields = ['title', 'subject', 'content', 'is_scheduled', 'scheduled_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Newsletter title',
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Email subject line',
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Newsletter content (HTML allowed)',
                'class': 'form-control',
                'rows': 15
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'subject',
            'content',
            Row(
                Column(
                    Field('is_scheduled', css_class='form-check-input'),
                    css_class='form-group col-md-6 mb-0'
                ),
                Column('scheduled_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Newsletter', css_class='btn btn-primary'),
            Submit('send_now', 'Save & Send Now', css_class='btn btn-success ml-2')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        is_scheduled = cleaned_data.get('is_scheduled')
        scheduled_date = cleaned_data.get('scheduled_date')
        
        if is_scheduled and not scheduled_date:
            raise forms.ValidationError("Please provide a scheduled date when scheduling is enabled.")
        
        return cleaned_data


class NewsletterPreviewForm(forms.Form):
    """Form for previewing newsletter before sending"""
    preview_email = forms.EmailField(
        label="Send preview to:",
        widget=forms.EmailInput(attrs={
            'placeholder': 'your-email@example.com',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'preview_email',
            Submit('submit', 'Send Preview', css_class='btn btn-info')
        )
