from django import forms 
from .models import Aluno

#class LoginForm(forms.ModelForm):
#    class Meta:
#        model = Aluno
#        fields = ['cpf', 'senha']
#        labels = {'cpf': 'Login', 'senha': 'Senha'}
        
class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

