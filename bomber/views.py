from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View

from .forms import *
from .utils import *
from attack import attack

from loguru import logger

class BomberIndex(DefaultViewMixin, View):
    template_name = "bomber/index.html"

class Register(SendFormMixin, View):
    template_name = "bomber/register.html"
    form = RegisterForm
    reverse_name = "index_url"
    choice = "REGISTER"

class Login(SendFormMixin, View):
    template_name = "bomber/login.html"
    form = LoginForm
    reverse_name = "index_url"
    choice = "LOGIN"

def panel(request):
    if request.method == "POST":
        f = AttackForm(request.POST)
        if f.is_valid and f.isValid():
            save = f.save()

            phone = f.cleaned_data.get("phone")
            work_time = f.cleaned_data.get("minute")
            # description = f.cleaned_data.get("description")
            attack.Bomber(phone, work_time, save.id).launch()
            return redirect("success")
        return render(request, "bomber/panel.html", {"form": f})
    return render(request, "bomber/panel.html", {"form": AttackForm()})

def success(request):
    return HttpResponse("Успешно запустил атаку на номер")