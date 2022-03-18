from django import forms

from .models import listings

class CreateListForm(forms.ModelForm):
    class Meta:
        model = listings
        fields = ['name', 'details', 'category', 'price', 'itempic']
        widgets = {
            'name' : forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Item name'}),
            'details' : forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Details'}),
            'category' : forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Category'}),
            'price' : forms.NumberInput(attrs={'required': True, 'class': 'form-control'}),
            'itempic' : forms.FileInput(attrs={'class': 'form-control-file'}),
        }