# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from core.forms import LoginForm, IssueForm, FilterDateForm, TimeEntryEdit, AddTimerForm
from core.models import Timer, TimeEntry
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from redmine_auth import settings
from django.http import HttpResponse, Http404
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
        if entries:
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
    return redirect(reverse(view_home))


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
                tracker = issue.tracker
                try:
                    timer = Timer.objects.get(user=request.user, redmine_issue_id=number_issue)
                except Timer.DoesNotExist:
                    timer = Timer(user=request.user, redmine_issue_id=number_issue,
                                  name=str(issue), project=project_name, tracker=tracker)
                    timer.save()
                return redirect(reverse(view_timer, kwargs={'timer_id': timer.id}))
            except Exception, e:
                messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_home))


@login_required(login_url=LOGIN_URL)
def view_timer(request, timer_id):
    add_timer_form = AddTimerForm()
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    return render(request, URL_RENDER['view_timer'], locals())


@login_required(login_url=LOGIN_URL)
def download_time_entries(request, timer_id):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        redmine = request.session['session_redmine']
        redmine_issue = redmine.issue.get(timer.redmine_issue_id)
        for entry in redmine_issue.time_entries:
            if entry.user.id == request.user.redmineuser.redmine_user_id:
                    try:
                        time_entry = TimeEntry.objects.get(user=request.user, redmine_timentry_id=entry.id,
                                                           timer=timer)
                        time_entry.time = entry.hours
                        time_entry.date = entry.spent_on
                        time_entry.comments = entry.comments
                        time_entry.is_synchronize = True
                        time_entry.save()
                    except TimeEntry.DoesNotExist:
                        created_entry = TimeEntry(user=request.user, timer=timer, redmine_timentry_id=entry.id,
                                                  time=entry.hours, comments=entry.comments, date=entry.spent_on,
                                                  is_synchronize=True)
                        created_entry.save()
        messages.info(request, "Time entrie(s) successful imported/updated !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))


@login_required(login_url=LOGIN_URL)
def upload_time_entries(request, timer_id, times_entries=[]):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        redmine = request.session['session_redmine']
        if not times_entries:
            times_entries = timer.timeentry_set.all()
        for entry in times_entries:
            if entry.redmine_timentry_id:
                try:
                    redmine.time_entry.update(entry.redmine_timentry_id, issue_id=timer.redmine_issue_id,
                                              spent_on=str(entry.date), hours=entry.time, comments=entry.comments)
                    entry.is_synchronize = True
                    entry.save()
                except ResourceNotFoundError:
                    entry.delete()
                except Exception, e:
                    raise e
            else:
                #TODO Create time entry on redmine
                pass
        messages.info(request, "Time entrie(s) successful uploaded !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))


@login_required(login_url=LOGIN_URL)
def refresh_issue(request, timer_id):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        redmine = request.session['session_redmine']
        issue = redmine.issue.get(timer.redmine_issue_id)
        timer.project = issue.project.name
        timer.tracker = issue.tracker
        timer.save()
        messages.info(request, "Issue successful refresed !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))


@login_required(login_url=LOGIN_URL)
def edit_entry(request, timer_id, entry_id):
    add_timer_form = AddTimerForm()
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        edit_entry = TimeEntry.objects.get(user=request.user, id=entry_id, timer=timer)
    except TimeEntry.DoesNotExist:
        raise Http404("Timer entry does not exist")
    try:
        if request.method == "POST":
            entry_edit_form = TimeEntryEdit(request.POST)
            if entry_edit_form.is_valid():
                date = entry_edit_form.cleaned_data['date']
                time = entry_edit_form.cleaned_data['time']
                comments = entry_edit_form.cleaned_data['comments']
                edit_entry.date = date
                edit_entry.time = time
                edit_entry.comments = comments
                edit_entry.is_synchronize = False
                edit_entry.save()
                return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))
        else:
            entry_edit_form = TimeEntryEdit(initial={
                'date': edit_entry.date,
                'time': edit_entry.time,
                'comments': edit_entry.comments,
            })
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return render(request, URL_RENDER['view_timer'], locals())


@login_required(login_url=LOGIN_URL)
def delete_entry(request, timer_id, entry_id):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        entry = TimeEntry.objects.get(user=request.user, id=entry_id, timer=timer)
    except TimeEntry.DoesNotExist:
        raise Http404("Timer entry does not exist")
    try:
        if entry:
            if entry.redmine_timentry_id:
                redmine = request.session['session_redmine']
                try:
                    delete_on_redmine = redmine.time_entry.delete(entry.redmine_timentry_id)
                except ResourceNotFoundError:
                    pass
                except Exception, e:
                    raise e
            entry.delete()
            messages.info(request, "Time entry successful deleted !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))


@login_required(login_url=LOGIN_URL)
def upload_entry(request, timer_id, entry_id):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        entry = TimeEntry.objects.get(user=request.user, id=entry_id, timer=timer)
    except TimeEntry.DoesNotExist:
        raise Http404("Timer entry does not exist")
    upload_time_entries(request, timer.id, [entry])
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))

@login_required(login_url=LOGIN_URL)
def add_timer(request, timer_id):
    try:
        timer = Timer.objects.get(user=request.user, id=timer_id)
    except Timer.DoesNotExist:
        raise Http404("Timer does not exist")
    try:
        if request.method == "POST":
            add_timer_form = AddTimerForm(request.POST)
            if add_timer_form.is_valid():
                time = add_timer_form.cleaned_data['time_hidden']
                if time <= 900:
                    time = 900 / 3600.
                else:
                    time /= 3600.
                created_entry = TimeEntry(user=request.user, timer=timer, time=time, date=datetime.now(),
                                          is_synchronize=False)
                created_entry.save()
                messages.info(request, "Time entrie successful created !", extra_tags='alert-success')
    except Exception, e:
        messages.error(request, e.message, extra_tags='alert-danger')
    return redirect(reverse(view_timer, kwargs={'timer_id': timer_id}))