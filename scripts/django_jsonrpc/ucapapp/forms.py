from django import forms

class UploadImgForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
