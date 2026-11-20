from django import forms

from .models import Resource
from .validators import validate_resource_url


class ResourceForm(forms.ModelForm):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'e.g. CS3012 Past Papers 2022',
    }))
    # Keep the entered scheme instead of silently adding https:// to bare input.
    url = forms.CharField(max_length=500, validators=[validate_resource_url],
                          widget=forms.URLInput(attrs={
                              'class': 'form-control',
                              'placeholder': 'https://drive.google.com/...',
                          }))
    category = forms.ChoiceField(choices=Resource.Category.choices,
                                 widget=forms.Select(attrs={'class': 'form-select'}))
    description = forms.CharField(required=False, max_length=500,
                                  widget=forms.Textarea(attrs={
                                      'class': 'form-control', 'rows': 2,
                                      'placeholder': 'Optional: briefly describe what this contains',
                                  }))

    class Meta:
        model = Resource
        fields = ('title', 'url', 'category', 'description')
