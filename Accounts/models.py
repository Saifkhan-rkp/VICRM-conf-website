from django.db import models
from django.utils.timezone import now
from accounts import constants
# Create your models here.django.utils.timezone.now
class User(models.Model):
    email = models.TextField(null=False,primary_key=True)
    password = models.TextField()
    type = models.TextField(null=False)

    
class Conference(models.Model):
    name = models.TextField(null=False,primary_key=True)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    abstract_submission_deadline = models.DateTimeField(null=False)
    paper_submission_deadline = models.DateTimeField(null=False)
    review_deadline = models.DateTimeField(null=False)

class Chair(models.Model):
    email = models.TextField(null=False,primary_key=True)
    password = models.TextField()
    name = models.TextField(null=False)
    is_accepted = models.BooleanField(default=False)

class Author(models.Model):
    email = models.TextField(null=False, primary_key=True)
    password = models.TextField()
    name = models.TextField(null=False)

class Reviewer(models.Model):
    email = models.TextField(null=False, primary_key=True)
    password = models.TextField()
    name = models.TextField(null=False)
    is_accepted = models.BooleanField(default=False)

class Paper(models.Model):
    name = models.TextField(null=False)
    paper_file_path = models.TextField(null=True)
    status = models.TextField(default=constants.PAPAERSUBMIT_INITIAL)
    author = models.ForeignKey('Author',on_delete=models.CASCADE)
    abstract_file_path = models.TextField(null=False)
    upload_date = models.DateTimeField(default= now)

#relationships
class Submits(models.Model):
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE)
    submit_date = models.DateTimeField(default= now)
    submit_status = models.TextField(default=constants.PAPERSUBMIT_ABSTRACT_PENDING)
    is_scheduled = models.BooleanField(default=False)



class Creates(models.Model):
    chair = models.ForeignKey('Chair', on_delete=models.CASCADE)
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE)

class Assigns(models.Model):
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE)
    chair = models.ForeignKey('Chair', on_delete=models.CASCADE)
    reviewer = models.ForeignKey('Reviewer', on_delete=models.CASCADE)
    conference = models.ForeignKey('Conference',on_delete=models.CASCADE)
    class Meta:
        unique_together = ('paper','reviewer')

class Reviews(models.Model):
    review_text_abstract = models.TextField(null=True)
    review_text_paper = models.TextField(null=True)
    reviewer = models.ForeignKey('Reviewer', on_delete=models.CASCADE)
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('paper','reviewer')

class Schedules(models.Model):
    chair = models.ForeignKey('chair', on_delete=models.CASCADE)
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE)
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE)