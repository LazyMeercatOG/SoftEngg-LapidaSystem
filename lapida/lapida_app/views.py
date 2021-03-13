from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import (
    CreateUserForm,
    ProfileForm,
    Order_UserForm,
    EventForm,
)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .decorators import unathenticated_user, allowed_users
from django.contrib.auth.models import Group
from .models import (
    User_Place,
    MasterData_Revised,
    CareTaker,
    Order_User,
    Caretaker_Task,
)
from .resources import MasterData_RevisedResource
from django.core.exceptions import ObjectDoesNotExist
import sweetify


def index(request):
    if request.user.is_authenticated:
        group = request.user.groups.all()[0].name
        if "caretaker" in group:
            return redirect("dashboard")
    return render(request, "lapida_app/index.html")


@unathenticated_user
def loginPage(request):
    message_error = ""
    message_error_1 = ""
    if request.user.is_authenticated:
        return redirect("home-view")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home-view")
            else:
                message_error = messages.info(
                    request, "Username or Password is incorrect"
                )
                message_error_1 = "Username or Password is incorrect"
        context = {"message_error": message_error_1}
        return render(request, "lapida_app/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


@unathenticated_user
def register(request):
    if request.user.is_authenticated:
        return redirect("home-view")
    else:
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            form_1 = ProfileForm(request.POST)
            gender = request.POST.get("gender")
            form_1.gender = gender
            if form.is_valid() and form_1.is_valid():
                user = form.save()
                form_1 = form_1.save(commit=False)
                group = Group.objects.get(name="customer")
                user.groups.add(group)
                form_1.user = user
                form_1.save()
                # Auto login and once authenticated then redirect to register dead page
                user = authenticate(
                    request,
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                )
                if user is not None:
                    login(request, user)
                    return redirect("create-dead")
        else:
            form = CreateUserForm()
            form_1 = ProfileForm()
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
                print(msg)
        context = {"form": form, "form_1": form_1}
        return render(request, "lapida_app/register.html", context)


@login_required(login_url="login")
def create_dead(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cemetery = request.POST.get("cemetery")
        dead_profile = []
        query_results = User_Place.objects.filter(user=request.user)
        for dead in query_results:
            dead_profile.append(MasterData_Revised.objects.get(uid=dead))
        try:
            person = MasterData_Revised.objects.get(
                place=cemetery,
                first_name=form.cleaned_data.get("first_name"),
                middle_name=form.cleaned_data.get("middle_name"),
                last_name=form.cleaned_data.get("last_name"),
                birthdate=form.cleaned_data.get("birth_date"),
            )
            if person in dead_profile:
                sweetify.error(
                    request,
                    "The person you inputted is already registered to your account.",
                    persistent=":(",
                )
                return redirect("create-dead")
        except MasterData_Revised.DoesNotExist:
            sweetify.error(
                request,
                "The person you inputted was not found in our database please try again.",
                persistent=":(",
            )
            return redirect("create-dead")
        instance = User_Place(uid=person)
        instance.user = request.user
        instance.save()
        return redirect("profile")
    else:
        form = EventForm()
    context = {"form": form}
    return render(request, "lapida_app/register_dead.html", context)


@allowed_users(allowed_roles=["caretaker"])
@login_required(login_url="login")
def dashboard(request):
    caretaker_profile = CareTaker.objects.get(user=request.user)
    caretaker_task = Caretaker_Task.objects.filter(caretaker=caretaker_profile)
    tasks = []
    for task in caretaker_task:
        tasks.append(Order_User.objects.get(caretaker_task=task))
    context = {"form": tasks}
    return render(request, "lapida_app/dashboard.html", context)


@login_required(login_url="login")
def menu(request):
    query_results = User_Place.objects.filter(user=request.user)
    form = Order_UserForm(request.POST)
    dead_profile = []
    for dead in query_results:
        dead_profile.append(MasterData_Revised.objects.get(uid=dead))
    if not dead_profile:
        messages.error(
            request, "Please register a profile of your loved one first."
        )
        return redirect("create-dead")
    context = {"form": dead_profile, "order": form}
    if request.method == "POST":
        current_price = 0
        options = []
        uid = request.POST.get("uid")
        instance = Order_User(
            profile_dead=User_Place.objects.get(user=request.user, uid=uid)
        )
        for x in range(6, 10):
            check = request.POST.get("customCheck" + str(x))
            if check:
                if x == 7:
                    flower = request.POST.get("customRadio")
                    current_price = get_flower_price(flower, current_price)
                    options.append(get_flower(flower))
                else:
                    options.append(get_options(x))
                    current_price = get_prices(x, current_price)
        if form.is_valid():
            order_date = form.cleaned_data.get("order_date")
            instance.order_date = order_date
            note = request.POST.get("Note")
            options = "\n".join(options)
            instance.status = "P"
            instance.price = current_price
            instance.services = options
            instance.note = note
            instance.save()
            profile_dead = MasterData_Revised.objects.get(
                uid=instance.profile_dead.uid
            )
            dead_place = get_cemetery(profile_dead.place)
            caretaker_profile = CareTaker.objects.filter(cemetery=dead_place)
            caretaker_p = []
            for i in caretaker_profile:
                caretaker_p.append(i)
            caretaker_task_instance = Caretaker_Task(caretaker=caretaker_p[0])
            caretaker_task_instance.order = instance
            caretaker_task_instance.save()
            return redirect("summary", instance.id)
    return render(request, "lapida_app/menu.html", context)


def get_cemetery(place):
    if place == "Manila North C":
        final_place = "MN"
    elif place == "Manila South C":
        final_place = "MS"
    elif place == "La Loma C":
        final_place = "L"
    elif place == " Manila Chinese C":
        final_place = "MC"
    return final_place


def get_options(x):
    if x == 6:
        option = "Service includes grass-trimming, watering the entire site, and proper cleaning the gravestone. Photos of before and after proof of service will be sent to your email."
    elif x == 8:
        option = "Placing of candle lights for the ones you love as an act of an extension for your prayers.Photos of before and after proof of service will be sent to your email."
    elif x == 9:
        option = "Haven's Memory will offer 'The Eternal Rest prayer' which is offered at any time during business hours for those who have departed in this life. "
    return option


def get_flower(flower):
    if flower == "Wreath":
        option = "Floral Arrangement: Wreath"
    elif flower == "Classic":
        option = "Floral Arrangement: Classic"
    elif flower == "Elegant":
        option = "Floral Arrangement: Elegant"
    return option


def get_prices(x, current_price):
    if x == 6:
        price = 3000 + current_price
    elif x == 8:
        price = 500 + current_price
    elif x == 9:
        price = 1500 + current_price
    return price


def get_flower_price(flower, current_price):
    if flower == "Wreath":
        price = 3000 + current_price
    elif flower == "Classic":
        price = 4000 + current_price
    elif flower == "Elegant":
        price = 6600 + current_price
    return price


@login_required(login_url="login")
def delete_record(request, uid):
    dead_profile = User_Place.objects.get(user=request.user, uid=uid)
    dead_profile.delete()


@login_required(login_url="login")
def profile(request):
    query_results = User_Place.objects.filter(user=request.user)
    dead_profile = []
    order_user = []
    order_query = []
    for dead in query_results:
        dead_profile.append(MasterData_Revised.objects.get(uid=dead))
        order_query += Order_User.objects.filter(profile_dead=dead)
    for order in order_query:
        try:
            order_user.append(Order_User.objects.get(id=order.id))
        except ObjectDoesNotExist:
            pass
    if not dead_profile:
        messages.error(
            request, "Please register a profile of your loved one first."
        )
        return redirect("create-dead")
    context = {"form": dead_profile, "order_user": order_user}
    return render(request, "lapida_app/profile.html", context)


@login_required(login_url="login")
def summary(request, id):
    order = Order_User.objects.get(id=id)
    context = {"form": order}
    return render(request, "lapida_app/summary.html", context)


def approve_payment(request, id):
    order = Order_User.objects.get(id=id)
    print(order)
    order.status = "Pa"
    order.save()
    context = {"form": order}
    return render(request, "lapida_app/summary.html", context)


def no_permission(request):
    return render(request, "lapida_app/no_permission.html")


def update_picture(request, id):
    if request.method == "POST":
        print("POST")
        order = Order_User.objects.get(id=id)
        order.image = request.FILES["image"]
        order.save()
        context = {"form": order}
        return render(request, "lapida_app/summary.html", context)


def update_status(request, id):
    order = Order_User.objects.get(id=id)
    if order.status == "Pa":
        order.status = "O"
    elif order.status == "O":
        order.status = "C"
    order.save()
    context = {"form": order}


def export(request):
    member_resource = MasterData_RevisedResource()
    dataset = member_resource.export()
    # response = HttpResponse(dataset.csv, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="member.csv"'
    # response = HttpResponse(dataset.json, content_type='application/json')
    # response['Content-Disposition'] = 'attachment; filename="persons.json"'
    response = HttpResponse(
        dataset.xls, content_type="application/vnd.ms-excel"
    )
    response["Content-Disposition"] = 'attachment; filename="persons.xls"'
    return response


def handle404(request, exception):
    return render(request, "lapida_app/404.html", status=404)


# Create your views here.
