from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from core.forms import LoginForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

URL_RENDER = {
    'view_login': 'core/login.html',
}


@login_required(login_url='/login')
def home(request):
    return HttpResponse("It's Home. <br /> <a href='/test'>Test</>")


@login_required(login_url='/login')
def test(request):
    return HttpResponse("It's Test. <br /> <a href='/'>Home</>")


def view_login(request):
    error = False
    next = request.REQUEST.get('next', '/')

    login_form = LoginForm()

    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(next)
            else:
                error = True
    return render(request, URL_RENDER['view_login'], locals())
