from django import forms


class UploadFile(forms.Form):
    """Simple form to handle a file uploading"""
    file = forms.FileField()
