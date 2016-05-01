# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, UserManager


def get_first_last_name(self):
    return '%s %s' % (self.first_name, self.last_name)

User.add_to_class("__str__", get_first_last_name)


class Event(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    descr = models.TextField()
    about = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to="logos", null=True, blank=True)

    def __str__(self):
        return '%s' % self.name

    def to_json(self):
        return dict(
            event_name=self.name,
            start_date=self.start_date,
            end_date=self.end_date,
            descr=self.descr,
            about=self.about,
        )

    class Meta:
        ordering = ['-start_date']


class MyUserManager(UserManager):


    #
    # def create_user(self, username, email=None, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', False)
    #     extra_fields.setdefault('is_superuser', False)
    #     return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username,  password,  **extra_fields):
        email = None
        u = self._create_user(username, email, password,  **extra_fields)
        u.is_superuser = True
        u.is_staff = True
        u.save(using=self._db)
        return u

class MyUser(AbstractUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    phone = models.CharField(max_length=40, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars", null=True, blank=True)
    is_speaker = models.BooleanField(default=False)

    objects = MyUserManager()

    def image_tag(self):  # to show image in admin http://stackoverflow.com/questions/2443752/django-display-image-in-admin-interface
        if self.avatar:
            return u'<img src="%s" />' % self.avatar.url

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def image_thumb(self):
        if self.avatar:
            return '<img src="%s" width="70" height="70" />' % (self.avatar.url)
    image_thumb.allow_tags = True

    def to_json(self):
        if not self.avatar:
            avatar_url = None
        else:
            avatar_url = self.avatar.url
        return dict(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            bio=self.bio,
            avatar=avatar_url,
        )


class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    SCHEDULE_TYPE = (
        ('SP', u'выступление'),
        ('BR', u'перерыв'),
        ('MA', u'основное'),
    )

    type = models.CharField(choices=SCHEDULE_TYPE, max_length=50)
    name = models.CharField(max_length=200)
    descr = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    speaker = models.ForeignKey(MyUser)

    def __str__(self):
        return '%s' % self.name

    def to_json(self):
        return dict(
            type=self.type,
            name=self.name,
            start_date=self.start_date,
            end_date=self.end_date,
            descr=self.descr,
            speaker_pk=self.speaker.pk,
            speaker_name=self.speaker.first_name+" "+self.speaker.last_name,
        )

    class Meta:
        ordering = ['start_date']


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    is_active = models.BooleanField()

    def __str__(self):
        return '%s' % self.question_text

    def to_json(self):
        choices = Choice.objects.filter(question=self)
        choices_dict = {}
        for c in choices:
            choices_dict[c.pk] = c.choice_text
        return dict(
            question_text=self.question_text,
            is_active=self.is_active,
            choices=choices_dict
            )


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return '%s' % self.choice_text

    def to_json(self):
        return dict(
            pk=self.pk,
            choice_text = self.self
            )

class Vote(models.Model):
    user = models.ForeignKey(MyUser)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)



# class CustomUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     phone = models.CharField(max_length=20)
#
#     USER_TYPE = (
#         ('AT', u'гость'),
#         ('BS', u'спикер'),
#         ('EA', u'администратор события'),
#     )
#     type = models.CharField(choices=USER_TYPE, max_length=50)
#     event = models.ForeignKey(Event)
#     bio = models.TextField(null=True, blank=True)
#
#     def __str__(self):
#         return '%s %s' % (self.user.first_name, self.user.last_name)
#
#     def to_json(self):
#         return dict(
#             first_name=self.user.first_name,
#             last_name=self.user.last_name,
#             bio=self.bio,
#             phone=self.phone,
#             some_other_information='some_other_information',
#         )