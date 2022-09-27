from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from .models import (
    User,
)
from .utils import (
    MAKE_PASSWORD,
    CHECK_PASSWORD,
    IsLoggedIn,
)

# Create your views here.

def index(request):
    return render(request, "index.html")

def upload(request):
    return render(request, "upload.html")

def stats(request):
    return render(request, "stats.html")

def login(request): 
    user = IsLoggedIn(request)
    if user is None:
        return render(request, "login.html")
    else:
        url = "/dashboard"
        return HttpResponseRedirect(url)

def loginUser(request): 
    user = IsLoggedIn(request)
    if user is None:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if CHECK_PASSWORD(password, user.password):
                    request.session["username"] = username
                    request.session.modified = True
                    url = "/dashboard"
                    return HttpResponseRedirect(url)
                else:
                    messages.error(request, "Incorrect password!")
                    return HttpResponseRedirect("/login") 
            else:
                messages.error(request, "User does not exist. Kindly register yourself! ")
                return HttpResponseRedirect("/login")
        else:
            messages.error(request, "Please fill in the credentials first to login in!")
            return HttpResponseRedirect("/login")
    else:
        url = "/dashboard"
        return HttpResponseRedirect(url)


def logout(request):
    if IsLoggedIn(request) is not None:
        del request.session["username"]
    return HttpResponseRedirect("/")

def signup(request):
    user = IsLoggedIn(request)
    if user is None:
        return render(request, "signup.html")
    else:
        url = "/dashboard"
        return HttpResponseRedirect(url)

def register(request):
    user = IsLoggedIn(request)
    if user is None:
        if request.method == "POST":
            name = request.POST.get("name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password")
            password2 = request.POST.get("conf_password")
            if(password1 != password2):
                messages.error(request, "Password does not match!")
                return HttpResponseRedirect("/signup")   
            else:
                password = MAKE_PASSWORD(password1)
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already in use!")
                    return HttpResponseRedirect("/signup")
                elif User.objects.filter(email=email).exists():
                    messages.error(request, "User with this email already exists!")
                    return HttpResponseRedirect("/signup")
                else:
                    user = User()
                    user.name = name
                    user.username = username
                    user.email = email
                    user.password = password
                    user.save()

                    messages.success(request, "User account created successfully!")
                    return HttpResponseRedirect("/login")
        else:
            messages.error(request, "Please fill in the credentials to sign up!")
            return HttpResponseRedirect("/signup")
    else: 
        url = "/dashboard"
        return HttpResponseRedirect(url)

def dashboard(request):
    return render(request, "dashboard.html")
