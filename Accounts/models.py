
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# import io
from datetime import date

# import pyavagen
# from django.conf import settings
# from django.contrib.auth.base_user import AbstractBaseUser
# from django.contrib.auth.models import PermissionsMixin
# from django.core.files.base import ContentFile

from django.dispatch import receiver
#from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _

# from .managers import UserManager

class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)

# class User(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(verbose_name=_('Email address'), unique=True)

#     date_joined = models.DateTimeField(
#         verbose_name=_('Date joined'),
#         auto_now_add=True
#     )

#     is_active = models.BooleanField(
#         verbose_name=_('Active'),
#         default=True
#     )

#     has_finished_registration = models.BooleanField(
#         default=False
#     )

#     objects = UserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')

#     # TODO: uncomment this later:
#     # def get_absolute_url(self):
#     #     return reverse('user-detail', kwargs={'pk': self.id})

#     def __str__(self):
#         return f'{self.pk}: {self.email}'


# class Profile(models.Model):
#     ROLES = (
#         (None, _('Select your role')),
#         ('Student', _('Student')),
#         ('PhD Student', _('PhD Student')),
#         ('Faculty Member',_('Faculty Member')),
#         ('International Delegates',_('International Delegates')),
#         ('Industry Person',_('Industry Person')),
#         ('Academician',_('Academician')),
#         ('PhD Scholar', _('PhD Scholar')),
#     )

#     STUDENT_ROLES = ('Student', 'PhD Student')
#     User_Roles = ((None, _('Select your role')),
#         ('Author',_('Author')),
#         ('Reviewer',_('Reviewer')),
#         ('Chair',_('Chair'))
#     )

#     #FACULTY_ROLES= ('')

#     DEGREE = (
#         (None, _('Select your degree')),
#         ('Undergraduate', _('Undergraduate')),
#         ('Bachelor', _('Bachelor')),
#         ('Master', _('Master')),
#         ('PhD', _('PhD')),
#         ('Candidate of Sciences', _('Candidate of Sciences')),
#         ('Doctor of Sciences', _('Doctor of Sciences')),
#     )
#     LANGUAGES = (
#         ('ENG', _('English')),
        
#     )

#     user = models.OneToOneField(User, on_delete=models.CASCADE)

#     first_name = models.CharField(
#         max_length=100, verbose_name=_("First Name ")
#     )
#     last_name = models.CharField(
#         max_length=100, verbose_name=_("Last Name ")
#     )
#     country = CountryField(null=True, verbose_name=_("Country"))
#     city = models.CharField(max_length=100, verbose_name=_("City"))
#     birthday = models.DateField(verbose_name=_("Birthday"), null=True)
#     affiliation = models.CharField(
#         max_length=100, verbose_name=_("Name of your organization"),
#     )
#     role = models.CharField(
#         choices=ROLES, max_length=30, null=True,
#         verbose_name=_('Primary role in organization')
#     )
#     degree = models.CharField(
#         choices=DEGREE, max_length=30, null=True,
#         verbose_name=_('Degree')
#     )
#     Conf_Role = models.CharField(choices=User_Roles, null=True, max_length= 30,
#         verbose_name=('Conference Role')
#     )

#     preferred_language = models.CharField(
#         choices=LANGUAGES, max_length=3, default='ENG'
#     )
#     is_Author = models.BooleanField(blank=True,default=False)
#     is_Chair = models.BooleanField(blank=True,default=False)
#     is_Reviewer = models.BooleanField(blank=True,default=False)
#     @property
#     def email(self):
#         return self.user.email

#     def get_short_name(self):
#         return self.first_name

#     def get_full_name(self):
#         return f'{self.first_name} {self.last_name}'

#     def age(self):
#         today = date.today()
#         born = self.birthday
#         rest = 1 if (today.month, today.day) < (born.month, born.day) else 0
#         return today.year - born.year - rest

#     def is_student(self):
#         return self.role in self.STUDENT_ROLES

#     def __str__(self):
#         return self.get_full_name()



# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         profile = Profile.objects.create(user=instance)
#         #profile.avatar = generate_avatar(profile)
#         #Subscriptions.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
#     #instance.subscriptions.save()