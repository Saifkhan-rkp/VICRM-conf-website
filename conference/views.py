from django.contrib.auth import authenticate,login
from django.shortcuts import redirect, render,HttpResponse
from .models import Speakers,Site_Settings
from .models import About_Conference as about
# from .forms import Info_Profile_Form, User_registration_Form
from django.contrib.auth.models import User
# from django.contrib import messages
# Create your views here.
def index(request,*args, **kwargs):
    Spk_object = Speakers.objects.all()
    setting = Site_Settings.objects.get(id=1)
    
    context={
        'speaker' : Spk_object,
        'setters' : setting,
    }
    #print(Spk_object.get(1))
    return render(request,'index.html',context)

def About_Conference(request,*args, **kwargs):
    
    context={
        'about':about.objects.all(),
    }
    return render(request,'aboutConfr.html',context)

def contact(request):
    return render(request,'contact.html')

def location(request):
    return render(request,'location.html')

def paper_submission(request):
    return render(request,'ppr-submsn.html')

def schedule(request):
    return render(request,'schedule.html')

