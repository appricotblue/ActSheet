from django import forms

class imgForm(forms.Form):
	image=forms.ImageField()

class imgForm1(forms.Form):
	image1=forms.ImageField()