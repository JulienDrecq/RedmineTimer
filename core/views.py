from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from core.forms import LoginForm, IssueForm
from core.models import Issue, TimeEntry
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from redmine_auth import settings
from django.http import HttpResponse
from django.db.models import Q
from redmine import Redmine
from redmine.exceptions import ForbiddenError, ResourceNotFoundError
import json
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

URL_RENDER = {
    'view_login': 'core/login.html',
    'view_home': 'core/home.html',
    'view_issue': 'core/issue.html',
}
LOGIN_URL = '/login'


@login_required(login_url=LOGIN_URL)
def view_home(request):
    issue_form = IssueForm()
    issues = Issue.objects.filter(Q(user_id=request.user)).order_by('id')
    return render(request, URL_RENDER['view_home'], locals())


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
                    next_url = reverse(start_new_timer) + "?number_issue=" + str(issue)
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
        number_issue = request.REQUEST.get('number_issue', False)
        if number_issue:
            try:
                issue = redmine.issue.get(int(number_issue))
                project_name = issue.project.name
                search_issue = Issue.objects.filter(Q(user=request.user, redmine_issue_id=number_issue,
                                                      date=datetime.now())).order_by('id')
                if search_issue:
                    issue = search_issue[0]
                    return redirect(reverse(view_issue, kwargs={'issue_id': issue.id}))
                else:
                    created_issue = Issue(user=request.user, redmine_issue_id=number_issue,
                                          name=str(issue), project=project_name)
                    created_issue.save()
            except ResourceNotFoundError:
                pass
            except Exception, e:
                pass
    return redirect(reverse(view_home))


@login_required(login_url=LOGIN_URL)
def view_issue(request, issue_id):
    issue = Issue.objects.filter(Q(user=request.user, id=issue_id))
    if not issue:
        return redirect(reverse(view_home), locals())
    issue = issue[0]
    return render(request, URL_RENDER['view_issue'], locals())


@login_required(login_url=LOGIN_URL)
def synchronize_time_entries(request, issue_id):
    issue = Issue.objects.filter(Q(user_id=request.user, id=issue_id))
    if not issue:
        return redirect(reverse(view_issue, kwargs={'issue_id': issue_id}), locals())
    issue = issue[0]
    return redirect(reverse(view_issue, kwargs={'issue_id': issue.id}), locals())


