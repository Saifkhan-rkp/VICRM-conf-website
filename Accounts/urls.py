from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'accounts'
urlpatterns = [
    #path('', views.index, name='index'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_up_handle', views.sign_up_handle, name='sign_up_handle'),
    path('login', views.login, name='login'),
    path('login_handle', views.login_handle, name='login_handle'),
    path('conferences',views.conferences, name="conferences"),
    path('add_conference_handle',views.add_conference_handle, name="add_conference_handle"),
    path('conference',views.conference,name='conference'),
    path('add_paper_handle',views.add_paper_handle,name='add_paper_handle'),
    path('logout',views.logout_handle,name='logou_handle'),
    path('accept_reject_chair_reviewer_handle',views.accept_reject_chair_reviewer_handle,name='accept_reject_chair_reviewer_handle'),
    path('chair_reviewer_application',views.chair_reviewer_application,name='chair_reviewer_application'),
    path('author_papers',views.author_papers,name="author_papers"),
    path('submit_paper',views.submit_paper,name='submit_paper'),
    path('assign_paper',views.assign_paper,name="assign_paper"),
    path('assign_paper_handle',views.assign_paper_handle,name="assign_paper_handle"),
    path('reviewer_assignments',views.reviewer_assignments,name='reviewer_assignments'),
    path('download_file',views.download_file,name="download_file"),
    path('add_review',views.add_review,name="add_review"),
    path('add_review_handle',views.add_review_handle,name="add_review_handle"),
    path('edit_review',views.edit_review,name='edit_review'),
    path('edit_review_handle',views.edit_review_handle,name='edit_review_handle'),
    path('paper_reviews',views.paper_reviews,name='paper_reviews'),
    path('paper_review',views.paper_review,name="paper_review"),
    path('accept_reject_paper',views.accept_reject_paper,name='accept_reject_paper'),
    path('paper',views.paper,name="paper"),
    path('update_paper_files',views.update_paper_files,name='update_paper_files'),
    path('schedule_conference',views.schedule_conference,name='schedule_conference'),
    path('schedule_paper_handle',views.schedule_paper_handle,name='schedule_paper_handle'),
    path('unschedule_paper_handle',views.unschedule_paper_handle,name='unschedule_paper_handle')
]