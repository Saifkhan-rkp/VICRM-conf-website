import datetime
from django.contrib.auth import authenticate,login
from django.shortcuts import redirect, render,HttpResponse
from .models import  Speakers,Site_Settings, Sponcer, Tickets
from .models import About_Conference as about
#from .forms import UserRegisterForm
# from .forms import Info_Profile_Form, User_registration_Form
from accounts import Utils
import hashlib
# Create your views here.
def check_login(request):
    if request.COOKIES.get('password'):
        return True
    else:
        return False
def check_admin_login(request):
    if request.COOKIES.get('password') == hash_string('admin') and request.COOKIES.get('user_type') == hash_string('admin'):
        return True
    else:
        return False
def hash_string(string):
    return hashlib.sha224(string.encode('utf-8')).hexdigest()

def create_login_cookies(response,email,hashed_password,non_hashed_user_type):
    max_age = 60 * 30
    hashed_user_type = hash_string(non_hashed_user_type)
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key="email", value=email, max_age=max_age, expires=expires)
    response.set_cookie(key="password", value=hashed_password, max_age=max_age, expires=expires)
    response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)





def index(request,*args, **kwargs):
    Spk_object = Speakers.objects.all()
    setting = Site_Settings.objects.get(id=1)
    Sponcer_object = Sponcer.objects.all()
    tickets = Tickets.objects.all()
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    context={
        'speaker' : Spk_object,
        'sponcer':Sponcer_object,
        'setters' : setting,
        "islogged_in":islogged_in,
        "is_admin_logged_in":is_admin_logged_in,
        "user_type":request.COOKIES.get('user_type'),
        'tickets':tickets,
    }
    #print(Spk_object.get(1))
    return render(request,'index.html',context)

def About_Conference(request,*args, **kwargs):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    print(request.COOKIES.get('user_type'))
    context={
        'about':about.objects.all(),
        "islogged_in":islogged_in,
        "is_admin_logged_in":is_admin_logged_in,
        "user_type":request.COOKIES.get('user_type'),
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

def registration(request):
    # if request.method == 'POST':
    #     profile_form = User_registration_Form(data=request.POST)
    #     info_form = Info_Profile_Form(data=request.POST)
    #     print(profile_form.is_valid() and info_form.is_valid)
    #     if profile_form.is_valid() and info_form.is_valid:
    #         user = profile_form.save()
    #         user.save()
    #         profile= info_form.save(commit=False)
    #         profile.user = user
    #         profile.save()
    #         return redirect('home')
    #     else:
    #         HttpResponse('Something galat hai')
    # else:
    #     profile_form =User_registration_Form(data=request.POST)
    #     inf_form = Info_Profile_Form(data=request.POST)
    return render (request,'login_Register.html',context={})


