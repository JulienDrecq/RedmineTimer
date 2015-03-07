from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from core.forms import LoginForm, IssueForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from redmine_auth import settings
from django.http import HttpResponse
from redmine import Redmine
from redmine.exceptions import ForbiddenError, ResourceNotFoundError
import json
import logging
logger = logging.getLogger(__name__)

URL_RENDER = {
    'view_login': 'core/login.html',
    'view_home': 'core/home.html',
}


@login_required(login_url='/login')
def view_home(request):
    issue_form = IssueForm()
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


@login_required(login_url='/login')
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


@login_required(login_url='/login')
def start_new_timer(request):
    if request.method == "GET":
        number_issue = request.REQUEST.get('number_issue', False)
        if number_issue:
            pass
    return redirect(reverse(view_home))

