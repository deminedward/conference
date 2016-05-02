# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import Textarea #, ModelForm

from event.models import *


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = MyUser
        # fields = UserCreationForm.Meta.fields + ('bio', 'event')
        fields = ('bio', 'event', 'avatar')


class MyUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = UserCreationForm.Meta.fields + ('bio', 'event', 'avatar', 'avatar')


class MyUserAdmin(UserAdmin):

    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_speaker', 'image_thumb')

    add_form = MyUserCreationForm
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'event', 'phone', 'avatar')}),
    )

    restricted_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'bio', 'avatar')}),
    )

    def save_model(self, request, obj, form, change): #TODO change for superuser. now superuser cannot creat event-admin
        if not request.user.is_superuser:
            obj.event = request.user.event
            obj.is_speaker = True
        obj.save()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return super(MyUserAdmin, self).get_fieldsets(request, obj=obj)
        else:
            if not request.user.is_superuser:
                return self.restricted_fieldsets
            else:
                return self.fieldsets

    #show only users, related to the event:
    def get_queryset(self, request):
        qs = super(MyUserAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if request.user.event:
                qs = qs.filter(event=request.user.event)
                print(qs)
                return qs
        else:
            return qs



    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     if request and not request.user.is_superuser:
    #                 if db_field.name == 'event':
    #                     qs = Event.objects.filter(customuser=request.user.customuser)
    #                     event = qs.first()
    #                     if event:
    #                         kwargs['initial'] = event.pk
    #                     kwargs['queryset'] = qs
    #             return super(ScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


def date_from_to(obj):
    return "%s %s-%s" % (obj.start_date.strftime("%d/%m/%Y"),
                         obj.start_date.strftime("%H:%M"),
                         obj.end_date.strftime("%H:%M"))


date_from_to.short_description = u'Когда'
date_from_to.admin_order_field = 'start_date'  # to sort by start_date, using that column


class ScheduleInline(admin.TabularInline):  # StackedInline or TabularInline
    model = Schedule
    #show TextField smaller:
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
            attrs={'rows': 1,
                   'cols': 30,
                   'style': 'height: 5em;'})},
    }

    def get_formset(self, request, obj=None, **kwargs):
        ScheduleInline.obj = obj
        return super(ScheduleInline, self).get_formset(request, obj, **kwargs)

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if start_date > end_date:
            raise forms.ValidationError("Dates are fucked up: start is later than the end")
        if start_date < self.obj.start_date or \
                        start_date > self.obj.end_date or \
                        end_date > self.obj.end_date or \
                        end_date < self.obj.start_date:
            raise forms.ValidationError("Dates are fucked up - outside the EVENT's dates")
        return self.cleaned_data

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'speaker':
            qs = MyUser.objects.filter(event=self.obj)
            kwargs['queryset'] = qs
            return super(ScheduleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


import os
import shutil
from shutil import copyfile
from django.conf import settings
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
BASE_DIR = getattr(settings, 'BASE_DIR')


def make_app(modeladmin, request, queryset):
    event = queryset.first()
    speakers = MyUser.objects.filter(event=event)
    dir_name = str(event.pk) + '_event'
    dir_path = os.path.join(BASE_DIR, dir_name)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    os.mkdir(os.path.join(dir_path, 'avatars'))
    for s in speakers:
        if s.avatar:
            src = os.path.join(BASE_DIR, MEDIA_ROOT, s.avatar.name)
            dst = os.path.join(dir_path, s.avatar.name)
            copyfile(src, dst)

make_app.short_description = u"подготовить к обновлению приложения"


class EventAdmin(admin.ModelAdmin):
    def get_name(self):
        return self.name

    get_name.short_description = 'Название События'

    list_display = (get_name, date_from_to)
    inlines = [
        ScheduleInline,
    ]
    actions = [make_app]

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(myuser=request.user)
        return qs
#
#
# # get_list_select_related() - must be read!
#
class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'

    def clean(self):
        # print(self.__dict__)
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if start_date > end_date:
            raise forms.ValidationError("Dates are fucked up: start is later than the end")
        if start_date < self.cleaned_data['event'].start_date or \
                        start_date > self.cleaned_data['event'].end_date or \
                        end_date > self.cleaned_data['event'].end_date or \
                        end_date < self.cleaned_data['event'].start_date:
            raise forms.ValidationError("Dates are fucked up - outside the EVENT's dates")
        return self.cleaned_data


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'speaker')
    list_editable = ('name', 'start_date', 'end_date', 'speaker') #edit and save multiple rows
    ordering = ['start_date']

    # date_hierarchy = 'start_date'

    def get_queryset(self, request):
        qs = super(ScheduleAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(event__myuser=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request and not request.user.is_superuser:
            if db_field.name == 'event':
                qs = Event.objects.filter(myuser=request.user)
                event = qs.first()
                if event:
                    kwargs['initial'] = event.pk
                kwargs['queryset'] = qs
        return super(ScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    form = ScheduleAdminForm

class ChoiceInline(admin.TabularInline):  # StackedInline or TabularInline
    model = Choice

    def get_formset(self, request, obj=None, **kwargs):
        ScheduleInline.obj = obj
        return super(ChoiceInline, self).get_formset(request, obj, **kwargs)
    #TODO - skeaker == current assigned speaker for schedule


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
    ]

    def get_queryset(self, request):
        qs = super(QuestionAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            # event = Event.objects.filter(user=)
            return qs.filter(schedule__event=request.user.event)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request and not request.user.is_superuser:
            if db_field.name == 'schedule':
                qs = Schedule.objects.filter(event=request.user.event)
                schedule = qs.first()
                if schedule:
                    kwargs['queryset'] = schedule.pk
                kwargs['queryset'] = qs
        return super(QuestionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
# class ChoiceAdmin(admin.ModelAdmin):
#     pass
#
#
# class VoteAdmin(admin.ModelAdmin):
#     pass
#
#


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice, ChoiceAdmin)
# admin.site.register(Vote, VoteAdmin)


# class CustomUserAdmin(admin.ModelAdmin):
#     def get_field_queryset(self, db, db_field, request):
#         pass
#
#     # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
#     #     if db_field.name == 'user':
#     #         # print(request.__dict__)
#     #         print(self.form)
#     #         # qs = obj.user
#     #         # kwargs['queryset'] = qs
#     #     return super(CustomUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             return ('user',)
#         return ()
#
#         # readonly_fields = ('user',)
#         # def user_added_at(self, obj):
#         #     return obj.user.added_at