from django.contrib import admin
from django.urls import path
from conference import views
#from django.conf import settings
#from django.conf.urls.static import static
app_name = 'conference'
urlpatterns = [
    path('',views.index, name ='home'),
    path('index',views.index, name ='index'),
    path('About_Conference',views.About_Conference, name ='About_Conference'),
    path('contact',views.contact, name ='contact'),
    path('location',views.location, name ='location'),
    path('paper_submission',views.paper_submission, name ='paper_submission'),
    path('schedule',views.schedule, name ='schedule'),
    #path('registration',views.register, name ='registration'),
    

]
#urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)