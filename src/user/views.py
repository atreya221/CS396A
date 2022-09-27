from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "index.html")

def upload(request):
    return render(request, "upload.html")

def stats(request):
    return render(request, "stats.html")

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def dashboard(request):
    return render(request, "dashboard.html")
