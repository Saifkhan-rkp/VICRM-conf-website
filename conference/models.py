#from conference.views import index
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.   usr: hell pass: hayhey
class Site_Settings(models.Model):
    site_title    = models.CharField(max_length=80) 
    hero_title    = models.CharField(max_length=80)
    hero_subtitle = models.CharField(max_length=120)

    #For footer
    footer_contact_no   = models.CharField(max_length=13)
    footer_contact_mail = models.EmailField()
    footer_FB_link      = models.CharField(max_length=500,blank=True)
    footer_tweeter_link = models.CharField(max_length=500,blank=True)
    footer_insta_link   = models.CharField(max_length=500,blank=True)
    footer_gleplus_link = models.CharField(max_length=500,blank=True)

class Speakers(models.Model):
    
    Speaker_Name     = models.CharField(max_length=50)
    Speaker_Position = models.CharField(max_length=50)
    About_speaker    = models.TextField(max_length=400)
    Speaker_Image    = models.ImageField(upload_to='images/speaker')
    
    #contact
    FB_link      = models.CharField(max_length=300,blank=True)
    tweeter_link = models.CharField(max_length=300,blank=True)
    insta_link   = models.CharField(max_length=300,blank=True)
    personal_link = models.CharField(max_length=300,blank=True)

    def __str__(self):
        return self.Speaker_Name

class Patrons(models.Model):
    Patron_Name     = models.CharField(max_length=50)
    Patron_Position = models.CharField(max_length=50)
    work_position   = models.CharField(max_length=50)
    About_Patron    = models.TextField(max_length=400)
    Patron_Image    = models.ImageField()
    
    #contact
    FB_link      = models.CharField(max_length=300,blank=True)
    tweeter_link = models.CharField(max_length=300,blank=True)
    insta_link   = models.CharField(max_length=300,blank=True)
    personal_link = models.CharField(max_length=300,blank=True)

    def __str__(self):
        return 'Patron : '+self.Patron_Name

class Sponcer(models.Model):
    Name           = models.CharField(max_length=100)
    Sponcer_logo   = models.ImageField()
    About_sponcers = models.TextField(blank=True)
    Sponcer_contact_link   = models.URLField(blank=True)

    def __str__(self):
        return 'Sponcer : '+self.Name

class Tickets(models.Model):
    Category_Name = models.CharField(max_length=80)
    Price         = models.DecimalField(decimal_places=2,max_digits=7000)
    Specification = models.TextField(blank=True)
    payment_link  = models.URLField(blank=True)

    def __str__(self):
        return 'For '+self.Category_Name

class About_Conference(models.Model):
    id = models.AutoField(primary_key=True,blank=False)
    heading = models.CharField(max_length=25)
    detail  = models.TextField()

    def __str__(self):
        return self.heading

class Instruction_For_Author(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField()

    def __str__(self):
        return self.title

class Paper(models.Model):
    name = models.TextField(null=False) 
    paper_file_path = models.TextField(null=True) 
    #status = models.TextField(default=constants.PAPAERSUBMIT_INITIAL)
    author = models.ForeignKey(User,on_delete=models.CASCADE,) 
    abstract_file_path = models.TextField(null=False) 
    upload_date = models.DateTimeField(default=timezone) 
 
#relationships 
class Paper_Submits(models.Model): 
    #conference = models.ForeignKey('Conference', on_delete=models.CASCADE) 
    author = models.ForeignKey(User, on_delete=models.CASCADE,) 
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE,) 
    submit_date = models.DateTimeField(default=timezone) 
    #submit_status = models.TextField(default=constants.PAPERSUBMIT_ABSTRACT_PENDING) 
    is_scheduled = models.BooleanField(default=False)