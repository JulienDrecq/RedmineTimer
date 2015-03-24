# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from core.forms import LoginForm, IssueForm, FilterDateForm
from core.models import Timer, TimeEntry
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from redmine_auth import settings
from django.http import HttpResponse
from django.db.models import Q
from redmine import Redmine
from redmine.exceptions import ForbiddenError, ResourceNotFoundError
import json
from datetime import datetime, timedelta
from core.templatetags.tools import get_week_days_range
import logging
logger = logging.getLogger(__name__)
from django.contrib import messages

URL_RENDER = {
    'view_login': 'core/login.html',
    'view_home': 'core/home.html',
    'view_timer': 'core/timer.html',
}
LOGIN_URL = '/login'


def get_entries(user, current_week_start, current_week_end):
    res_entries = []
    while current_week_start != current_week_end:
        search_entries = TimeEntry.objects.filter(Q(user=user, date=current_week_start)).order_by('id')
        entries = {}
        time_total_day = 0
        date = current_week_start
        if date.today() == current_week_start:
            date = u"Today"
        elif date.today() - timedelta(days=1) == current_week_start:
            date = u"Yesterday"
        for entry in search_entries:
            time_total_day += entry.time
            if entry.timer.id in entries:
                entries[entry.timer.id]['time_timer'] += entry.time
            else:
                entries.update({entry.timer.id: {'timer': entry.timer, 'time_timer': entry.time}})
        res_entries.append({'date': date, 'entries': entries, 'time_total_day': time_total_day})
        current_week_start += timedelta(days=1)
    res_entries.reverse()
    return res_entries


@login_required(login_url=LOGIN_URL)
def view_home(request):
    page_name = "Timeline of the week"
    issue_form = IssueForm()
    filter_date_form = FilterDateForm()
    current_calandar = datetime.now().isocalendar()
    last_calendar = (datetime.now() - timedelta(days=7)).isocalendar()
    current_week_start, current_week_end = get_week_days_range(current_calandar[0], current_calandar[1])
    last_week_start, last_week_end = get_week_days_range(last_calendar[0], last_calendar[1])
    res_entries = get_entries(request.user, current_week_start, current_week_end)
    return render(request, URL_RENDER['view_home'], locals())


@login_required(login_url=LOGIN_URL)
def from_to_time_entries(request, start_date, end_date):
    issue_form = IssueForm()
    filter_date_form = FilterDateForm()
    current_start = datetime.strptime(start_date, '%Y-%m-%d').date()
    current_end = datetime.strptime(end_date, '%Y-%m-%d').date()
    page_name = "Timeline from %s to %s" % (current_start, current_end)
    if current_start > current_end:
        messages.error(request, "Date expected", extra_tags='alert-danger')
        return render(request, URL_RENDER['view_home'], locals())
    res_entries = get_entries(request.user, current_start, current_end)
    return render(request, URL_RENDER['view_home'], locals())


@login_required(login_url=LOGIN_URL)
def filter_date(request):
    filter_date_form = FilterDateForm()

    if request.method == "POST":
        filter_date_form = FilterDateForm(request.POST)
        if filter_date_form.is_valid():
            start_date = filter_date_form.cleaned_data['start_date']
            end_date = filter_date_form.cleaned_data['end_date']
            return redirect(reverse(from_to_time_entries, kwargs={'start_date': start_date,
                                                                  'end_date': end_date}))
    return redirect(reverse(view_home), locals())


def view_login(request):
    if request.user.is_authenticated():
        return redirect(reverse(view_home), locals())
    error = False
    next = request.REQUEST.get('next', '/')

    login_form = LoginForm()

    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                redmine = Redmine(settings.REDMINE_SERVER_URL, username=username, password=password)
                request.session['session_redmine'] = redmine
                request.session['name'] = str(redmine.auth())
                return redirect(next)
            else:
                error = True
    return render(request, URL_RENDER['view_login'], locals())


def view_logout(request):
    logout(request)
    return redirect(reverse(view_login))


@login_required(login_url=LOGIN_URL)
def new_timer(request):
    if request.is_ajax():
        if request.method == "POST":
            issue_form = IssueForm(request.POST)
            if issue_form.is_valid():
                issue = issue_form.cleaned_data['issue']
                result = {'error': False, 'value_error': ''}
                try:
                    redmine = request.session['session_redmine']
                    number_issue = "#" + str(issue)
                    link_issue = settings.REDMINE_SERVER_URL + "/issues/" + str(issue)
                    next_url = reverse(start_new_timer) + "?issue=" + str(issue)
                    issue = redmine.issue.get(int(issue))
                    project_name = issue.project.name
                    result.update({'issue': str(issue), 'number-issue': number_issue, 'link-issue': link_issue,
                                   'project-issue': project_name, 'next-url': next_url})
                except ForbiddenError:
                    result.update({'error': True})
                    result.update({'value_error': 'Forbidden access on issue !'})
                except ResourceNotFoundError:
                    result.update({'error': True})
                    result.update({'value_error': 'Issue not found !'})
                except Exception, e:
                    logger.error('Error in search issue : %s' % e)
                    result.update({'error': True})
                    result.update({'value_error': 'An error has occurred !'})
                return HttpResponse(json.dumps(result), content_type="application/json")
        else:
            return redirect(reverse(view_home))
    else:
        return redirect(reverse(view_home))


@login_required(login_url=LOGIN_URL)
def start_new_timer(request):
    redmine = request.session['session_redmine']
    if request.method == "GET":
        number_issue = request.REQUEST.get('issue', False)
        if number_issue:
            try:
                issue = redmine.issue.get(int(number_issue))
                project_name = issue.project.name
                search_timer = Timer.objects.filter(Q(user=request.user,
                                                      redmine_issue_id=number_issue)).order_by('id')
                if search_timer:
                    timer = search_timer[0]
                    return redirect(reverse(view_timer, kwargs={'timer_id': timer.id}))
                else:
                    created_timer = Timer(user=request.user, redmine_issue_id=number_issue,
                                          name=str(issue), project=project_name)
                    created_timer.save()
                    return redirect(reverse(view_timer, kwargs={'timer_id': created_timer.id}))
            except Exception, e:
                messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_home))


@login_required(login_url=LOGIN_URL)
def view_timer(request, timer_id):
    timer = Timer.objects.filter(Q(user=request.user, id=timer_id))
    if not timer:
        return redirect(reverse(view_home), locals())
    timer = timer[0]
    return render(request, URL_RENDER['view_timer'], locals())


@login_required(login_url=LOGIN_URL)
def download_time_entries(request, timer_id):
    timer = Timer.objects.filter(Q(user_id=request.user, id=timer_id))
    if not timer:
        return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}), locals())
    timer = timer[0]
    try:
        redmine = request.session['session_redmine']
        redmine_issue = redmine.issue.get(timer.redmine_issue_id)
        for entry in redmine_issue.time_entries:
            if entry.user.id == request.user.redmineuser.redmine_user_id:
                search_entry = TimeEntry.objects.filter(Q(user=request.user, redmine_timentry_id=entry.id,
                                                          timer=timer)).order_by('id')
                if search_entry:
                    timeentry = search_entry[0]
                    timeentry.time = entry.hours
                    timeentry.date = entry.spent_on
                    timeentry.comments = entry.comments
                    timeentry.save()
                else:
                    created_entry = TimeEntry(user=request.user, timer=timer, redmine_timentry_id=entry.id,
                                              time=entry.hours, comments=entry.comments, date=entry.spent_on)
                    created_entry.save()
        messages.info(request, "Time entries successful imported/upated !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer.id}), locals())


@login_required(login_url=LOGIN_URL)
def upload_time_entries(request, timer_id):
    timer = Timer.objects.filter(Q(user_id=request.user, id=timer_id))
    if not timer:
        return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}), locals())
    timer = timer[0]
    try:
        redmine = request.session['session_redmine']
        for entry in timer.timeentry_set.all():
            if entry.redmine_timentry_id:
                redmine.time_entry.update(entry.redmine_timentry_id, issue_id=timer.redmine_issue_id,
                                          spent_on=str(entry.date), hours=entry.time, comments=entry.comments)
            else:
                #TODO Create time entry on redmine
                pass
        messages.info(request, "Time entries successful uploaded !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}), locals())