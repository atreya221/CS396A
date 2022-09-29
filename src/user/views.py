from http.client import HTTPResponse
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from .models import (
    User,
    FileForm,
)
from .utils import (
    MAKE_PASSWORD,
    CHECK_PASSWORD,
    IsLoggedIn,
)
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

# Create your views here.

def index(request):
    user = IsLoggedIn(request)
    if user is not None:
        return HttpResponseRedirect("/dashboard")
    else:
        return render(request, "index.html")

def upload(request):
    user = IsLoggedIn(request)
    if user is None:
        messages.error(request, "Please login first to upload files!")
        return HttpResponseRedirect("/login")
    else:
        return render(request, "upload.html")

def submitForm(request):
        user = IsLoggedIn(request)
        if user is None: 
            messages.error(request, "Please login first to upload files!")
            return HttpResponseRedirect("/login")
        else: 
            if request.method == "POST":
                form = FileForm()
                form.user = User.objects.get(username=IsLoggedIn(request).username)
                form.organization = request.POST.get("name")
                form.file = request.FILES["file"]
                form.save()
                return HttpResponseRedirect("/dashboard")
            else:
                return HttpResponseRedirect("/login")

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
    user = IsLoggedIn(request)
    if user is None:
        messages.error(request, "Please login first to view dashboard!")
        return HttpResponseRedirect("/login")
    else:
        return render(
            request,
            "dashboard.html",
            {
                "user": IsLoggedIn(request),
                "files": FileForm.objects.filter(user=IsLoggedIn(request)).order_by('-file_id'),
            },
        )

class UploadView(CreateView):
    model = FileForm
    fields = ['file', ]
    success_url = reverse_lazy('fileupload')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = FileForm.objects.all()
        return context

def deleteFile(request):
    user = IsLoggedIn(request)
    if user is None:
        messages.error(request, "Please login first to delete file!")
        return HttpResponseRedirect("/login")
    else:
        file_id = request.GET.get("file_id")
        # print(file_id)
        FileForm.objects.filter(file_id=file_id).delete()
        return HttpResponseRedirect("/dashboard")