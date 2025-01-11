# forms.py
from django import forms

class PhotoUploadForm(forms.Form):
    photo = forms.ImageField(
        label='Выберите фотографию',
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )