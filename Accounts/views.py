from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse,Http404
from accounts import models
import hashlib
from accounts import Utils
from threading import Lock
from threading import Thread
from VICRM import settings
import datetime
from django.core.files.storage import FileSystemStorage
import os
from accounts import constants
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import smart_str
from django.shortcuts import redirect

email_lock = Lock()

#utility funcs
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
#view funcs

def download_file(request):
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')
    if file_type == "abstract":
        path_to_file = settings.MEDIA_URL+"abstracts/" + file_name
    else:
        path_to_file = settings.MEDIA_URL+ "papers/" + file_name
    if os.path.exists(path_to_file):
        with open(path_to_file, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_to_file)
            return response
    raise Http404

def index(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    return render(request,"index.html",{"islogged_in":islogged_in,"is_admin_logged_in":is_admin_logged_in,"user_type":request.COOKIES.get('user_type')})

def sign_up(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    return render(request,"sign_up.html",{"islogged_in":islogged_in,"is_admin_logged_in":is_admin_logged_in,"user_type":request.COOKIES.get('user_type')})

def sign_up_handle(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    print(islogged_in)
    if request.method == "POST":
        # TODO add form checks here or in html as javascript
        user_type = request.POST.get('user_type')
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password').encode('utf-8')
        hashed_password = hashlib.sha224(password).hexdigest()
        context = {"islogged_in": False,"is_admin_logged_in":is_admin_logged_in,"user_type":request.COOKIES.get('user_type')}
        if user_type == "author":
            context['islogged_in'] = True
            user = models.User(email=email,password=hashed_password, type="author")
            user.save()
            author = models.Author(email=email,password=hashed_password, name=name)
            author.save()

            response = render(request, "sign_up_handle.html", context)
            create_login_cookies(response,email,author.password,'author')
            email_send_thread = Thread(target=Utils.send_email, args=("About your registration to conference management system",
                                                                       "You have been registered as an author",
                                                                      author.email,
                                                                       email_lock
                                                                       ))
            email_send_thread.start()

        else:
            response = render(request, "sign_up_handle.html", context)

            if user_type == "chair":
                is_chair = True
                user = models.User(email=email, password=hashed_password, type="chair")
                user.save()
                chair = models.Chair(email=email, password=hashed_password, name=name)
                chair.save()

            elif user_type == "reviewer":
                is_chair = False
                user = models.User(email=email, password=hashed_password, type="reviewer")
                user.save()
                reviewer = models.Reviewer(email=email, password=hashed_password, name=name)
                reviewer.save()
            email_send_thread = Thread(target=Utils.send_email_for_user_sign_up, args=(is_chair,
                                                                                       email,
                                                                                       email_lock
                                                                                       ))
            email_send_thread.start()
        return response

def login(request):
    app_url = request.path
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    context = {"islogged_in":islogged_in,'message':"",
    "is_admin_logged_in":is_admin_logged_in,
    "user_type":request.COOKIES.get('user_type'),
    'app_url': app_url
    }
    return render(request,"login.html", context)



def login_handle(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email == 'admin' and password == 'admin':
            chairs = models.Chair.objects.all()
            reviewers = models.Reviewer.objects.all()
            context = {"islogged_in":True,"is_admin_logged_in":True,"chairs":chairs,
                                                                         "reviewers":reviewers,"user_type":request.COOKIES.get('user_type')}
            response = render(request,"chair_reviewer_application.html",context)
            hashed_admin_password = hash_string('admin')
            create_login_cookies(response,'admin',hashed_admin_password,'admin')
            return response
        else:
            password = password.encode('utf-8')
            hashed_password = hashlib.sha224(password).hexdigest()
            user_type = None
            max_age = 60 * 30
            try:
                user = models.User.objects.get(email=email,password=hashed_password)
                user_type = user.type
                try:
                    hashed_user_type = hashlib.sha224(user_type.encode('utf-8')).hexdigest()
                    context = {"islogged_in":True,"user_type":hash_string(user_type)}
                    response = render(request, "index.html",context)
                    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                                         "%a, %d-%b-%Y %H:%M:%S GMT")


                    response.set_cookie(key="email", value=email, max_age=max_age, expires=expires)
                    if user_type == "chair":
                        chair = models.Chair.objects.get(email=email,password=hashed_password)
                        response.set_cookie(key="password", value=chair.password, max_age=max_age, expires=expires)
                        response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)

                    elif user_type == "reviewer":
                        reviewer = models.Reviewer.objects.get(email=email, password=hashed_password)
                        response.set_cookie(key="password", value=reviewer.password, max_age=max_age, expires=expires)
                        response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)
                    elif user_type == "author":
                        author = models.Author.objects.get(email=email, password=hashed_password)
                        response.set_cookie(key="password", value=author.password, max_age=max_age, expires=expires)
                        response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)
                    return response
                except Exception as e:
                    return HttpResponse("Unexpected error. Exception : ",e)
            except Exception as e:
                # Non existing user
                print(e)
                return render(request,"login.html",{"islogged_in":True,'message':'Bad Authentication.',"is_admin_logged_in":is_admin_logged_in
                                                    ,"user_type":request.COOKIES.get('user_type')})


def logout_handle(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    response = render(request, "index.html", {"islogged_in": False,"is_admin_logged_in":False})
    response.delete_cookie('user_type')
    response.delete_cookie('email')
    response.delete_cookie('password')
    return response
def conferences(request):
    islogged_in = check_login(request)
    is_admin_logged_in = check_admin_login(request)
    confs = models.Conference.objects.all()
    hashed_user_type = hash_string('chair')

    #checck if the user is chair
    if request.COOKIES.get('user_type') == hashed_user_type:
        #then check if it is approved
        chair = models.Chair.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
        is_accepted = chair.is_accepted
    else:
        is_accepted = False
    time_now = timezone.now()


    return render(request,"conferences.html",{"islogged_in":islogged_in,"confs":confs,
                                              "user_type":request.COOKIES.get('user_type'),
                                                  "chair_hashed_user_type":hashed_user_type,
                                              "is_accepted":is_accepted,
                                              "is_admin_logged_in":is_admin_logged_in,
                                              "time_now":time_now
                                              })

def add_conference_handle(request):
    if request.method == "POST":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        hashed_user_type = hashlib.sha224("chair".encode('utf-8')).hexdigest()

        start_date = datetime.datetime.strptime(request.POST.get('start_date'), '%Y-%m-%dT%H:%M')
        end_date = datetime.datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M')
        abstract_submission_deadline = datetime.datetime.strptime(request.POST.get('abstract_submission_deadline'),
                                                               '%Y-%m-%dT%H:%M')
        paper_submission_deadline = datetime.datetime.strptime(request.POST.get('paper_submission_deadline'), '%Y-%m-%dT%H:%M')
        review_deadline = datetime.datetime.strptime(request.POST.get('review_deadline'),
                                                               '%Y-%m-%dT%H:%M')
        name = request.POST.get('name')
        if request.COOKIES.get('user_type') == hashed_user_type:
            # then check if it is approved
            chair = models.Chair.objects.get(email=request.COOKIES.get('email'),
                                             password=request.COOKIES.get('password'))
            is_accepted = chair.is_accepted
        else:
            is_accepted = False
        chair = models.Chair.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
        conference = models.Conference(name=name,start_date=start_date,end_date=end_date,abstract_submission_deadline=abstract_submission_deadline,
                                       review_deadline=review_deadline,
                                       paper_submission_deadline=paper_submission_deadline)
        conference.save()
        authors = models.Author.objects.all()
        # for author in authors:
        #     email_send_thread = Thread(target=Utils.send_email, args=("A new conference has been added",
        #                                                               "Conference " + conference.name + " has been added",
        #                                                               author.email,
        #                                                               email_lock
        #                                                               ))
        #     email_send_thread.start()
        create_conference = models.Creates(chair=chair,conference=conference)
        create_conference.save()
        confs = models.Conference.objects.all()
        time_now = timezone.now()
        context = {"islogged_in":islogged_in,
        "confs":confs,
        "user_type":request.COOKIES.get('user_type'),
        "is_accepted": is_accepted,
        "hashed_user_type":hashed_user_type,
        "is_admin_logged_in":is_admin_logged_in,
        "time_now":time_now
        }
        return render(request,"conferences.html",context)

def schedule_conference(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:
            conf_name = request.GET.get('conf_name')
            conference = models.Conference.objects.get(name=conf_name)
            submits = models.Submits.objects.filter(conference=conference,submit_status=constants.PAPERSUBMIT_PAPER_ACCEPTED)
            schedules = models.Schedules.objects.filter(conference=conference)
            scheduled_papers = []
            last_schedule_time = conference.start_date
            unscheduled_papers = []
            for submit in submits:
                if not submit.is_scheduled:
                    unscheduled_papers.append(submit.paper)

            for schedule in schedules:
                scheduled_papers.append(
                    [schedule.paper, last_schedule_time, last_schedule_time + datetime.timedelta(minutes=30)])
                last_schedule_time = last_schedule_time + datetime.timedelta(minutes=45)
                scheduled_papers.append([None, last_schedule_time - datetime.timedelta(minutes=15), last_schedule_time])
                if last_schedule_time.time().hour >= 19:
                    scheduled_papers.pop()
                    last_schedule_time = last_schedule_time + datetime.timedelta(days=1)
                    last_schedule_time = datetime.datetime(year=last_schedule_time.year,
                                                           month=last_schedule_time.month,
                                                           day=last_schedule_time.day,
                                                           hour=conference.start_date.hour,
                                                           minute=conference.start_date.minute,
                                                           second=0)
            if len(scheduled_papers) != 0 and scheduled_papers[-1][0] == None:
                scheduled_papers.pop()

        return render(request, "schedule_conference.html",
                      {"islogged_in": islogged_in,
                       "scheduled_papers": scheduled_papers,
                       "unscheduled_papers": unscheduled_papers,
                       "user_type": request.COOKIES.get('user_type'),
                       "conf_name": conf_name,
                       "start_date": conference.start_date,
                       "end_date": conference.end_date,
                       "is_admin_logged_in": is_admin_logged_in})



def schedule_paper_handle(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:
            conf_name = request.GET.get('conf_name')
            paper_id = int(request.GET.get('paper_id'))
            conference = models.Conference.objects.get(name=conf_name)
            paper = models.Paper.objects.get(id=paper_id)
            submit_paper = models.Submits.objects.get(paper=paper,conference=conference)
            submit_paper.is_scheduled = True
            chair = models.Chair.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
            schedule = models.Schedules(conference=conference,paper=paper,chair=chair)
            schedule.save()
            submit_paper.save()
            return redirect('/schedule_conference?conf_name='+conf_name)

def unschedule_paper_handle(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:
            conf_name = request.GET.get('conf_name')
            paper_id = int(request.GET.get('paper_id'))
            conference = models.Conference.objects.get(name=conf_name)
            paper = models.Paper.objects.get(id=paper_id)
            submit_paper = models.Submits.objects.get(paper=paper,conference=conference)
            submit_paper.is_scheduled = False
            chair = models.Chair.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
            schedule = models.Schedules.objects.get(conference=conference,paper=paper,chair=chair)
            schedule.delete()
            submit_paper.save()
            return redirect('/schedule_conference?conf_name='+conf_name)

def conference(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        conference = models.Conference.objects.get(name=request.GET.get('conf_name'))
        submits_conf1 = models.Submits.objects.filter(conference=conference)
        submits_conf2 = []
        for submit in submits_conf1:
            paper = models.Paper.objects.get(id=submit.paper.id)
            can_accept_reject = False if not paper.paper_file_path and submit.submit_status in constants.PAPERSUBMIT_PAPER_PENDING else True

            submits_conf2.append([submit,can_accept_reject])
        author_hashed_user_type = hash_string('author')
        chair_hashed_user_type = hash_string('chair')

        available_papers = []

        if request.COOKIES.get('user_type') == author_hashed_user_type:

            author = models.Author.objects.get(email=request.COOKIES.get('email'),
                                               password=request.COOKIES.get('password'))
            if conference.abstract_submission_deadline > timezone.now():

                papers = models.Paper.objects.filter(Q(author=author),Q(status=constants.PAPAERSUBMIT_INITIAL))
                submits = models.Submits.objects.filter(Q(author=author),Q(submit_status=constants.PAPERSUBMIT_ABSTRACT_REJECTED) |
                                                               Q(submit_status=constants.PAPERSUBMIT_PAPER_REJECTED) )
                for paper in papers:
                    available_papers.append(paper)

            else:
                #means that the abstract submission deadline has passed
                #then if the author has a paper submitted to conference that is in status of abstract accepted or paper rejected can submit again.
                submits = models.Submits.objects.filter(Q(author=author),Q(conference=conference),
                                                    Q(submit_status=constants.PAPERSUBMIT_ABSTRACT_ACCEPTED) |
                                                    Q(submit_status=constants.PAPERSUBMIT_PAPER_REJECTED))

            for submit in submits:
                available_papers.append(submit.paper)

        return render(request, "conference.html",
                      {"islogged_in": islogged_in, "submits": submits_conf2, "user_type": request.COOKIES.get('user_type'),
                       "author_hashed_user_type": author_hashed_user_type,
                       "chair_hashed_user_type":chair_hashed_user_type,"conf_name":request.GET.get('conf_name'),"is_admin_logged_in":is_admin_logged_in,
                       "available_papers":available_papers,
                       "accept_strings":constants.PAPERSUBMIT_ABSTRACT_ACCEPTED + constants.PAPERSUBMIT_PAPER_ACCEPTED,
                       "reject_strings":constants.PAPERSUBMIT_ABSTRACT_REJECTED + constants.PAPERSUBMIT_PAPER_REJECTED,
                       "pending": constants.PAPERSUBMIT_PAPER_PENDING + constants.PAPERSUBMIT_ABSTRACT_PENDING,
                       "accepted": constants.PAPERSUBMIT_PAPER_ACCEPTED + constants.PAPERSUBMIT_ABSTRACT_ACCEPTED,
                       "rejected": constants.PAPERSUBMIT_ABSTRACT_REJECTED + constants.PAPERSUBMIT_PAPER_REJECTED
                       })




def accept_reject_chair_reviewer_handle(request):
    if request.method == "GET":
        is_admin_logged_in = check_admin_login(request)
        if is_admin_logged_in:
            is_accepted = request.GET.get('is_accepted')
            user_type = request.GET.get('user_type')
            user_mail = request.GET.get('user_mail')
            if is_accepted == "True":
                is_accepted = True
            else:
                is_accepted = False
            if user_type == "reviewer":
                reviewer = models.Reviewer.objects.get(email=user_mail)
                reviewer.is_accepted = (not is_accepted)
                reviewer.save()
                if is_accepted:
                    message = "You have been deauthorised in VICRM Conference as a reviewer."
                else:
                    message = "You have been authorised in VICRM Conference as a reviewer."
            elif user_type == "chair":
                chair = models.Chair.objects.get(email=user_mail)
                chair.is_accepted = (not is_accepted)
                chair.save()
                if is_accepted:
                    message = "You have been deauthorised in VICRM Conference as a chair."
                else:
                    message = "You have been authorised in VICRM Conference as a chair."
            email_send_thread = Thread(target=Utils.send_email, args=("Your status in VICRM conference.",
                                                                                       message,
                                                                                       user_mail,
                                                                                       email_lock
                                                                                       ))
            email_send_thread.start()
            chairs = models.Chair.objects.all()
            reviewers = models.Reviewer.objects.all()
            response = render(request, "chair_reviewer_application.html",
                              {"islogged_in":True,"is_admin_logged_in": True, "chairs": chairs, "reviewers": reviewers
                               ,"hashed_user_type":request.COOKIES.get('user_type'),
                               "user_type":request.COOKIES.get('user_type')})
            return response

def chair_reviewer_application(request):
    if request.method == "GET":
        is_admin_logged_in = check_admin_login(request)
        if is_admin_logged_in:
            chairs = models.Chair.objects.all()
            reviewers = models.Reviewer.objects.all()
            response = render(request, "chair_reviewer_application.html",
                              {"islogged_in":True,"is_admin_logged_in": is_admin_logged_in, "chairs": chairs, "reviewers": reviewers
                               ,"user_type":request.COOKIES.get('user_type')})
            return response

def author_papers(request):
    if request.method == "GET":
        is_logged_in = check_login(request)
        if not is_logged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('author'):
            return HttpResponse('You are not logged in as an author.')
        else:
            email = request.COOKIES.get('email')
            hashed_password = request.COOKIES.get('password')
            author = models.Author.objects.get(email=email, password=hashed_password)
            papers = models.Paper.objects.filter(author=author)
            papers_submits = []
            for paper in papers:
                try:
                    submit = models.Submits.objects.get(paper=paper)
                    papers_submits.append([paper,submit])
                except:
                    papers_submits.append([paper,None])

            response = render(request, "author_papers.html",
                              {"islogged_in": is_logged_in,"papers_submits":papers_submits
                                  , "user_type":request.COOKIES.get('user_type'),
                               "pending":constants.PAPERSUBMIT_PAPER_PENDING+constants.PAPERSUBMIT_ABSTRACT_PENDING,
                               "accepted":constants.PAPERSUBMIT_PAPER_ACCEPTED+constants.PAPERSUBMIT_ABSTRACT_ACCEPTED,
                               "rejected":constants.PAPERSUBMIT_ABSTRACT_REJECTED+constants.PAPERSUBMIT_PAPER_REJECTED})
            return response


def add_paper_handle(request):
    islogged_in = check_login(request)
    if not islogged_in:
        return HttpResponse("You are not logged in.")
    elif request.COOKIES.get('user_type') != hash_string('author'):
        return HttpResponse('You are not logged in as an author.')
    else:
        try:
            request.FILES['abstract_file']
        except:
            return HttpResponse("There is a problem with your abstract file. Try again.")
        if request.method == 'POST' and request.FILES['abstract_file']:
            is_admin_logged_in = check_admin_login(request)
            file_abstract = request.FILES['abstract_file']
            abstract_directory = 'Uploads/abstracts/'
            if not os.path.exists(abstract_directory):
                os.makedirs(abstract_directory)

            fs = FileSystemStorage(location=abstract_directory)  # defaults to   MEDIA_ROOT
            filename = fs.save(file_abstract.name, file_abstract)
            file_abstract_url = fs.url(filename)

            author = models.Author.objects.get(email=request.COOKIES.get('email'),
                                               password=request.COOKIES.get('password'))
            paper = models.Paper(name=request.POST.get('name'), paper_file_path=None,
                                 abstract_file_path=file_abstract_url, author=author)
            paper.save()

            papers = models.Paper.objects.filter(author=author)
            papers_submits = []
            for paper in papers:
                try:
                    submit = models.Submits.objects.get(paper=paper)
                    papers_submits.append([paper, submit])
                except:
                    papers_submits.append([paper, None])
            response = render(request, "author_papers.html",
                              {"islogged_in": islogged_in, "papers_submits": papers_submits,
                               "user_type": hash_string('author')
                                  , "user_type":request.COOKIES.get('user_type')})
            return response


def submit_paper(request):
    if request.method == "POST":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('author'):
            return HttpResponse('You are not logged in as an author.')
        else:
            paper_id = request.POST.get('paper_id')
            try:
                paper = models.Paper.objects.get(id=int(paper_id))
            except:
                return HttpResponse("Please choose a paper.")

            conf_name = request.POST.get('conf_name')
            conference = models.Conference.objects.get(name=conf_name)
            print(paper.status)
            if str(paper.status) != constants.PAPAERSUBMIT_INITIAL:
                #means that the paper is submitted before. handle the situations
                submit = models.Submits.objects.get(paper=paper)
                if submit.submit_status == constants.PAPERSUBMIT_ABSTRACT_REJECTED:
                    submit.submit_status = constants.PAPERSUBMIT_ABSTRACT_PENDING
                    submit.conference = conference
                elif submit.submit_status == constants.PAPERSUBMIT_PAPER_REJECTED:
                    if submit.conference == conference:
                        submit.submit_status = constants.PAPERSUBMIT_PAPER_PENDING
                    else:
                        submit.submit_status = constants.PAPERSUBMIT_ABSTRACT_PENDING
                        submit.conference = conference
                submit.save()
            else:
                submit = models.Submits(conference=conference,author=paper.author,paper=paper)
                submit.save()
            paper.status = constants.PAPAERSUBMIT_SUBMITTED
            paper.save()
        return render(request, "index.html", {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                                              "user_type": request.COOKIES.get('user_type')})

def assign_paper(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as an chair.')
        else:
            reviewers = models.Reviewer.objects.filter(is_accepted=True)
            paper = models.Paper.objects.get(id=int(request.GET.get('paper_id')))
            reviewers_assigns = []
            for reviewer in reviewers:
                try:
                    assign = models.Assigns.objects.get(paper=paper,reviewer=reviewer)
                    print(assign)
                    reviewers_assigns.append([reviewer,assign])
                except:
                    reviewers_assigns.append([reviewer,None])
        return render(request, "assign_paper.html", {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                                              "user_type": request.COOKIES.get('user_type'),
                                              "reviewers_assigns":reviewers_assigns,
                                                     "paper_id":request.GET.get('paper_id'),
                                                     "conf_name":request.GET.get('conf_name')})

def assign_paper_handle(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as an chair.')
        else:
            chair = models.Chair.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
            reviewer = models.Reviewer.objects.get(email=request.GET.get('reviewer_email'))
            paper = models.Paper.objects.get(id=int(request.GET.get('paper_id')))
            conference = models.Conference.objects.get(name=request.GET.get('conf_name'))
            assign = models.Assigns(chair=chair,reviewer=reviewer,paper=paper,conference=conference)
            assign.save()
            email_send_thread = Thread(target=Utils.send_email, args=("Your review assignment","You have been assigned paper name : " + paper.name + " for a review.",
                             reviewer.email,email_lock ))
            email_send_thread.start()

            reviewers = models.Reviewer.objects.filter(is_accepted=True)
            reviewers_assigns = []
            for reviewer in reviewers:
                try:
                    assign = models.Assigns.objects.get(paper=paper,reviewer=reviewer)
                    print(assign)
                    reviewers_assigns.append([reviewer,assign])
                except:
                    reviewers_assigns.append([reviewer,None])

        return render(request, "assign_paper.html", {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                                              "user_type": request.COOKIES.get('user_type'),
                                              "reviewers_assigns":reviewers_assigns,
                                                     "paper_id":request.GET.get('paper_id'),
                                                     "conf_name":request.GET.get('conf_name')})

def reviewer_assignments(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('reviewer'):
            return HttpResponse('You are not logged in as an reviewer.')
        else:
            reviewer = models.Reviewer.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
            assignments = models.Assigns.objects.filter(reviewer=reviewer)
            assignments_reviews = []
            for assignment in assignments:
                is_paper_uploaded = True if assignment.paper.paper_file_path  else False
                try:
                    review = models.Reviews.objects.get(paper=assignment.paper,reviewer=reviewer)

                    assignments_reviews.append([assignment,review,is_paper_uploaded])
                    print(is_paper_uploaded)
                except Exception as e:
                    print(e)
                    assignments_reviews.append([assignment,None,is_paper_uploaded])
            return render(request, "reviewer_assignments.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "assignments_reviews": assignments_reviews,
                           "time_now":timezone.now()})


def add_review(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('reviewer'):
            return HttpResponse('You are not logged in as an reviewer.')
        else:
            if request.GET.get('is_paper') == "True":

                review_id = request.GET.get('review_id')
                print(review_id)
            else:
                review_id = None
            return render(request, "add_review.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "paper_id": request.GET.get('paper_id'),
                           "is_paper":request.GET.get('is_paper'),
                           "review_id":review_id
                           })

def add_review_handle(request):
    if request.method == "POST":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('reviewer'):
            return HttpResponse('You are not logged in as a reviewer.')
        else:
            paper = models.Paper.objects.get(id=int(request.POST.get('paper_id')))
            review_text = request.POST.get('review_text')
            reviewer = models.Reviewer.objects.get(email=request.COOKIES.get('email'),password=request.COOKIES.get('password'))
            print(request.POST.get('review_id'))
            if request.POST.get('is_paper') == "True":
                review = models.Reviews.objects.get(id=int(request.POST.get('review_id')))
                review.review_text_paper = review_text
            else:
                review = models.Reviews(review_text_abstract=review_text,
                                        review_text_paper=None,
                                        reviewer=reviewer,paper=paper)
            review.save()
            assignments = models.Assigns.objects.filter(reviewer=reviewer)
            assignments_reviews = []
            for assignment in assignments:
                try:
                    review = models.Reviews.objects.get(paper=assignment.paper, reviewer=reviewer)
                    assignments_reviews.append([assignment, review])
                except:
                    assignments_reviews.append([assignment, None])
            return redirect("/reviewer_assignments")

def edit_review(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('reviewer'):
            return HttpResponse('You are not logged in as a reviewer.')
        else:
            try:

                review_id = request.GET.get('review_id')
                print(review_id)
            except:
                review_id = None
                print("none")
            review = models.Reviews.objects.get(id=int(request.GET.get('review_id')))
            return render(request, "add_review.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "paper_id": request.GET.get('paper_id'),
                           "review": review,
                           "is_paper":request.GET.get('is_paper'),
                           "review_id":review_id
                           })

def edit_review_handle(request):
    if request.method == "POST":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('reviewer'):
            return HttpResponse('You are not logged in as a reviewer.')
        else:

            print(request.POST.get('review_id'))
            review = models.Reviews.objects.get(id=int(request.POST.get('review_id')))
            if request.POST.get('is_paper') == "True":
                review.review_text_paper = request.POST.get('review_text')
            else:
                review.review_text_abstract = request.POST.get('review_text')
            review.save()
            reviewer = models.Reviewer.objects.get(email=request.COOKIES.get('email'),
                                                   password=request.COOKIES.get('password'))
            assignments = models.Assigns.objects.filter(reviewer=reviewer)
            assignments_reviews = []
            for assignment in assignments:
                try:
                    review = models.Reviews.objects.get(paper=assignment.paper, reviewer=reviewer)
                    assignments_reviews.append([assignment, review])
                except:
                    assignments_reviews.append([assignment, None])
            return redirect("/reviewer_assignments")

def paper_reviews(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:
            paper = models.Paper.objects.get(id=int(request.GET.get('paper_id')))
            reviews = models.Reviews.objects.filter(paper=paper)
            return render(request, "paper_reviews.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "reviews": reviews})

def paper_review(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:

            review = models.Reviews.objects.get(id=int(request.GET.get('review_id')))
            return render(request, "paper_review.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "review": review})

def accept_reject_paper(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('chair'):
            return HttpResponse('You are not logged in as a chair.')
        else:
            is_accepted = request.GET.get('is_accepted')
            submit = models.Submits.objects.get(id=int(request.GET.get('submit_id')))
            reviews = models.Reviews.objects.filter(paper=submit.paper)
            type = "abstract"
            accept_status = "accepted"
            if is_accepted == "True":
                accept_status = "accepted"
                if submit.submit_status == constants.PAPERSUBMIT_ABSTRACT_PENDING or submit.submit_status == constants.PAPERSUBMIT_ABSTRACT_REJECTED:
                    submit.submit_status = constants.PAPERSUBMIT_PAPER_PENDING
                    type = "abstract"
                elif submit.submit_status == constants.PAPERSUBMIT_PAPER_PENDING or submit.submit_status == constants.PAPERSUBMIT_PAPER_REJECTED:
                    submit.submit_status = constants.PAPERSUBMIT_PAPER_ACCEPTED
                    type = "paper"
            else:
                accept_status = "rejected"
                if submit.submit_status == constants.PAPERSUBMIT_ABSTRACT_PENDING or submit.submit_status == constants.PAPERSUBMIT_ABSTRACT_ACCEPTED:
                    submit.submit_status = constants.PAPERSUBMIT_ABSTRACT_REJECTED
                    type = "abstract"
                elif submit.submit_status == constants.PAPERSUBMIT_PAPER_PENDING or submit.submit_status == constants.PAPERSUBMIT_PAPER_ACCEPTED:
                    submit.submit_status = constants.PAPERSUBMIT_PAPER_REJECTED
                    type = "paper"
            submit.save()
            subject = "Update for your paper : " + submit.paper.name + " in conference " + submit.conference.name + "."
            message = "Your " + type + " for " + submit.paper.name + " has been " + accept_status + ".\n"
            if len(reviews) == 0:
                message += "There are no reviews for your paper.\n"
            else:
                for review in reviews:
                    message += "Review from " + review.reviewer.name + "\n"
                    if review.review_text_abstract and type == "abstract":
                        message += "Abstract review : \n" + review.review_text_abstract
                    if review.review_text_paper and type == "paper":
                        message += "Paper review : \n" + review.review_text_paper

            to = submit.paper.author.email
            Utils.send_email_with_thread(subject,message,to,email_lock)
        response = redirect('/conference?conf_name=' +request.GET.get('conf_name'))
        return response


def paper(request):
    if request.method == "GET":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('author'):
            return HttpResponse('You are not logged in as an author.')
        else:
            paper = models.Paper.objects.get(id=int(request.GET.get('paper_id')))
            can_update_abstract = False
            can_update_paper = False
            can_download_abstract = False
            can_download_paper = False
            try:
                time_now = timezone.now()
                submit = models.Submits.objects.get(paper=paper)
                paper_submission_deadline = submit.conference.paper_submission_deadline
                abstract_submission_deadline = submit.conference.abstract_submission_deadline
                if submit.submit_status in constants.PAPERSUBMIT_ABSTRACT_REJECTED+constants.PAPAERSUBMIT_INITIAL:
                    can_update_abstract = True
                    can_download_abstract = True
                elif submit.submit_status in constants.PAPERSUBMIT_PAPER_REJECTED:
                    can_download_abstract = True
                    can_update_paper = True
                    can_download_paper = True
                elif submit.submit_status in constants.PAPERSUBMIT_PAPER_PENDING:
                    if submit.paper.paper_file_path:
                        can_download_abstract = True
                        can_update_paper = False
                        can_download_paper = True
                    else:
                        can_download_abstract = True
                        can_update_paper = True
                        can_download_paper = True
                elif submit.submit_status in constants.PAPERSUBMIT_ABSTRACT_ACCEPTED:
                    can_download_abstract = True
                    can_update_paper = True
                elif submit.submit_status in constants.PAPERSUBMIT_PAPER_ACCEPTED:
                    can_download_abstract = True
                    can_download_paper = True
                if not paper.paper_file_path:
                    can_download_paper = False
                if time_now > abstract_submission_deadline:
                    can_update_abstract = False
                if time_now > paper_submission_deadline:
                    can_update_paper = False
                paper_submission_deadline_passed = timezone.now() > paper_submission_deadline
                abstract_submission_dealine_passed = timezone.now() > abstract_submission_deadline

            except:
                #means that the author has not submitted the paper to any conference
                can_update_abstract = True
                can_download_abstract = True


            return render(request, "paper.html",
                          {"islogged_in": islogged_in, "is_admin_logged_in": is_admin_logged_in,
                           "user_type": request.COOKIES.get('user_type'),
                           "can_update_abstract": can_update_abstract,
                           "can_download_abstract" : can_download_abstract,
                           "can_update_paper" : can_update_paper,
                           "can_download_paper" : can_download_paper,
                           "paper":paper,
                           "submit":submit,
                           "abstract_update_states":constants.PAPERSUBMIT_ABSTRACT_REJECTED+constants.PAPERSUBMIT_ABSTRACT_PENDING,
                           "paper_update_states":constants.PAPERSUBMIT_PAPER_PENDING+constants.PAPERSUBMIT_PAPER_REJECTED,
                           "abstract_states":constants.PAPERSUBMIT_ABSTRACT_PENDING+constants.PAPERSUBMIT_ABSTRACT_REJECTED,
                           "paper_status":paper.status,
                           "paper_submit_initial":constants.PAPAERSUBMIT_INITIAL,
                           "paper_submission_deadline_passed": paper_submission_deadline_passed,
                            "abstract_submission_dealine_passed":abstract_submission_dealine_passed})

def update_paper_files(request):
    if request.method == "POST":
        islogged_in = check_login(request)
        is_admin_logged_in = check_admin_login(request)
        if not islogged_in:
            return HttpResponse("You are not logged in.")
        elif request.COOKIES.get('user_type') != hash_string('author'):
            return HttpResponse('You are not logged in as an author.')
        else:
            paper = models.Paper.objects.get(id=int(request.POST.get('paper_id')))
            paper_directory = 'Uploads/papers/'
            abstract_directory = 'Uploads/abstracts/'
            if not os.path.exists(paper_directory):
                os.makedirs(paper_directory)
            if 'abstract_file' in request.FILES:
                os.remove(abstract_directory + paper.abstract_file_path)
                file_abstract = request.FILES['abstract_file']

                fs = FileSystemStorage(location=abstract_directory)  # defaults to   MEDIA_ROOT
                filename = fs.save(file_abstract.name, file_abstract)
                file_abstract_url = fs.url(filename)
                paper.abstract_file_path = file_abstract_url
            elif 'paper_file' in request.FILES:
                if paper.paper_file_path:
                    os.remove(paper_directory + paper.paper_file_path)
                file_paper = request.FILES['paper_file']
                fs = FileSystemStorage(location=paper_directory)  # defaults to   MEDIA_ROOT
                filename = fs.save(file_paper.name, file_paper)
                file_paper_url = fs.url(filename)
                paper.paper_file_path = file_paper_url

            else:
                return HttpResponse("Please choose a file")

            assigns = models.Assigns.objects.filter(paper=paper)
            print(len(assigns))
            for assign in assigns:
                Utils.send_email_with_thread("About your review assignment",
                                             "Your review assignment for paper : " + paper.name + " has uploaded a new version of their paper",
                                             assign.reviewer.email, email_lock)
            try:
                submit = models.Submits.objects.get(paper=paper)
                if submit.submit_status in constants.PAPERSUBMIT_PAPER_PENDING+constants.PAPERSUBMIT_PAPER_REJECTED:
                    submit.submit_status = constants.PAPERSUBMIT_PAPER_PENDING
                elif submit.submit_status in constants.PAPERSUBMIT_ABSTRACT_PENDING+constants.PAPERSUBMIT_ABSTRACT_REJECTED:
                    submit.submit_status = constants.PAPERSUBMIT_ABSTRACT_PENDING

                submit.save()
            except:
                pass
            paper.save()

        response = redirect('/paper?paper_id=' + str(paper.id))
        return response