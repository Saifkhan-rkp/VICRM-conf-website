from django import forms
from django.db.models.base import Model
#from django.forms import fields
#from .models import Profile
#from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#from conference import models

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
# class User_registration_Form(forms.ModelForm):
#     passeword = forms.CharField(widget=forms.PasswordInput())

#     class Meta():
#         model = User
#         fields=(
#             'username',
#             'email',
#             'password',
            
#         )
# class Info_Profile_Form(forms.ModelForm):
#     class Meta():
#         model = Profile
#         fields= (
#             'First_Name',
#             'Last_Name',
#             'Profile_type',
#             'Bio',
#             'is_Author',
#         )
    
   
# class PaperSubmissionForm(forms.ModelForm):
#     pass


        # user = super(UserRegistrationForm, self).save(commit=False)
        # user.email = self.cleaned_data['email']