# # from django import forms
# # from django.db.models.base import Model
# # #from django.forms import fields
# # #from .models import Profile
# # #from django.contrib.auth.models import User
# # from django.contrib.auth.forms import UserCreationForm
# # from django.contrib.auth.models import User

# # #from conference import models

# # class UserRegisterForm(UserCreationForm):
# #     email = forms.EmailField()

# #     class Meta:
# #         model = User
# #         fields = ['username', 'email', 'password1', 'password2']
        
# # # class User_registration_Form(forms.ModelForm):
# # #     passeword = forms.CharField(widget=forms.PasswordInput())

# # #     class Meta():
# # #         model = User
# # #         fields=(
# # #             'username',
# # #             'email',
# # #             'password',
            
# # #         )
# # # class Info_Profile_Form(forms.ModelForm):
# # #     class Meta():
# # #         model = Profile
# # #         fields= (
# # #             'First_Name',
# # #             'Last_Name',
# # #             'Profile_type',
# # #             'Bio',
# # #             'is_Author',
# # #         )
    
   
# # class PaperSubmissionForm(forms.ModelForm):
# #     pass


# #         # user = super(UserRegistrationForm, self).save(commit=False)
# #         # user.email = self.cleaned_data['email']


#     <h1 class="dccn-panel-title">Profile</h1>
#       {% include 'components/profile_navigation.html' with active='account' %}

#       <div class="dccn-content p-4">

#         {% bootstrap_messages %}

#         <h2 class="dccn-subtitle mb-3">Update Email</h2>
#         <form action="{% url 'users:update-email' %}" method="POST" class="form-inline dccn-protected-form" id="updateEmailForm">
#           {% csrf_token %}
#           <input type="email" name="email" id="newEmailInput" class="form-control flex-fill" placeholder="Current email: {{ user.email }}">
#           <button type="button" class="btn btn-outline-primary btn-sm ml-sm-2 mt-2 mt-sm-0" data-toggle="modal" data-target="#updateEmailConfirmDialog">Update</button>
#         </form>
#         <hr>

#         <h2 class="dccn-subtitle mb-3">Change Password</h2>
#         <form action="{% url 'users:update-password' %}" method="POST" class="dccn-protected-form" id="updatePasswordForm">
#           {% csrf_token %}
#           <div class="form-group">
#             <input type="password" name="new_password1" id="password1" class="form-control" placeholder="Enter new password">
#           </div>

#           <div class="form-group">
#             <input type="password" name="new_password2" id="password2" class="form-control" placeholder="Re-type your new password">
#             <div class="invalid-feedback">Passwords must match</div>
#           </div>

#           <button type="button" class="btn btn-outline-primary btn-sm" data-toggle="modal" data-target="#updatePasswordConfirmDialog">Update</button>
#         </form>
#         <hr>

#         <h2 class="dccn-subtitle mb-3">Notification Settings</h2>
#         <form action="{% url 'users:update-subscriptions' %}" method="POST" id="notificationsSettingsForm">
#           {% csrf_token %}
#           {% bootstrap_form notifications_form %}
#           <button type="submit" class="btn btn-outline-primary btn-sm">Update</button>
#         </form>
#         <hr>

#         <h2 class="dccn-subtitle mb-3">Danger Zone</h2>
#         <button class="btn btn-danger btn-sm" data-toggle="modal" data-target="#confirmDeleteAccount">Delete account</button>
#       </div>
#     </div>
#   </div>