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
from django.core.mail import send_mail, BadHeaderError
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from lapida.settings import EMAIL_HOST_USER
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
import datetime
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator


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
                if user.is_active:
                    login(request, user)
                    return redirect("home-view")
                else:
                    message_error_1 = None
                    sweetify.error(
                        request,
                        "Your account is not activated yet please check your email for the verification link",
                        persistent=":(",
                    )
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
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                form_1 = form_1.save(commit=False)
                group = Group.objects.get(name="customer")
                user.groups.add(group)
                form_1.user = user
                form_1.save()
                current_site = get_current_site(request)
                mail_subject = "Activate your account."
                message = render_to_string(
                    "lapida_app/verification.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                to_email = form.cleaned_data.get("email")
                send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
                message_error_1 = None
                sweetify.error(
                    request,
                    "You need to verify your account via email that we sent in order to login.",
                    persistent=":)",
                )
                context = {"message_error": message_error_1}
                return render(request, "lapida_app/login.html", context)
                # # Auto login and once authenticated then redirect to register dead page
                # user = authenticate(
                #     request,
                #     username=form.cleaned_data["username"],
                #     password=form.cleaned_data["password1"],
                # )
                # if user is not None:
                #     login(request, user)
                #     return redirect("create-dead")
        else:
            form = CreateUserForm()
            form_1 = ProfileForm()
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
        context = {"form": form, "form_1": form_1}
        return render(request, "lapida_app/register.html", context)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        message_error_1 = None
        user.save()
        sweetify.error(
            request,
            "Your account is activated go log in your account now!",
            persistent=":)",
        )
        context = {"message_error": message_error_1}
        return render(request, "lapida_app/login.html", context)
    else:
        return HttpResponse("Activation link is invalid!")


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
    caretaker_task_none = Caretaker_Task.objects.filter(caretaker=None)
    for task in caretaker_task_none:
        tasks.append(Order_User.objects.get(caretaker_task=task))
    context = {"form": tasks}
    return render(request, "lapida_app/dashboard.html", context)


@login_required(login_url="login")
def menu(request):
    query_results = User_Place.objects.filter(user=request.user)
    form = Order_UserForm(request.POST)
    dead_profile = []
    cemeteries = []
    for dead in query_results:
        person_dead = MasterData_Revised.objects.get(uid=dead)
        dead_profile.append(person_dead)
        cemeteries.append(person_dead.place)
    if not dead_profile:
        messages.error(request, "Please register a profile of your loved one first.")
        return redirect("create-dead")
    context = {"form": dead_profile, "order": form, "cemeteries": cemeteries}
    if request.method == "POST":
        id_to_check = ["graveCheck", "flowerCheck", "prayerCheck"]
        options = []
        for id in id_to_check:
            if request.POST.get(id):
                value = get_value_of_user_choices(request, id)
                options.append(value)
        uid = request.POST.get("uid")
        totalpay = request.POST.get("cat_id")
        instance = Order_User(
            profile_dead=User_Place.objects.get(user=request.user, uid=uid)
        )
        if form.is_valid():
            order_date = form.cleaned_data.get("order_date")
            instance.order_date = order_date
            note = request.POST.get("Note")
            options.append("₱" + str(totalpay))
            options.append(note)
            options = "\n".join(options)
            instance.status = "NT"
            instance.price = totalpay
            instance.services = options
            instance.note = note
            instance.save()
            profile_dead = MasterData_Revised.objects.get(uid=instance.profile_dead.uid)
            dead_place = get_cemetery(profile_dead.place)
            caretaker_profile = CareTaker.objects.filter(cemetery=dead_place)
            caretaker_p = []
            for i in caretaker_profile:
                caretaker_p.append(i)
            caretaker_task_instance = Caretaker_Task(caretaker=None)
            # User = get_user_model()
            # user = User.objects.get(pk=caretaker_p[0].user.id)
            # user_email = user.email
            # current_site = get_current_site(request)
            # mail_subject = "New Task"
            # message = render_to_string(
            #     "lapida_app/verification.html",
            #     {
            #         "user": user,
            #         "domain": current_site.domain,
            #         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            #         "token": account_activation_token.make_token(user),
            #     },
            # )
            # to_email = user_email
            # send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
            caretaker_task_instance.order = instance
            caretaker_task_instance.save()
            return redirect("summary", instance.id)
    return render(request, "lapida_app/menu.html", context)


def get_value_of_user_choices(request, id):
    if id == "graveCheck":
        option = ""
        if request.POST.get("gravecareCheck"):
            option += "Gravestone Care - ₱1000\n"
        if request.POST.get("landscapeCheck"):
            option += "Gravestone Care - ₱1000"
        return option
    elif id == "flowerCheck":
        option = ""
        flower = request.POST.get("flowerSelect")
        if flower:
            if flower == "citifora":
                flower_arrangement = request.POST.get("citiforaRadio")
                option += flower_arrangement
            elif flower == "gertudes":
                flower_arrangement = request.POST.get("gertudesRadio")
                option += flower_arrangement
            elif flower == "raphael":
                flower_arrangement = request.POST.get("raphaelRadio")
                option += flower_arrangement
            elif flower == "larose":
                flower_arrangement = request.POST.get("laroseRadio")
                option += flower_arrangement
            return option
    elif id == "prayerCheck":
        option = ""
        option += "Prayer Service and Candle Lighting - ₱1500"
        return option


def get_cemetery(place):
    if place == "Manila North C":
        final_place = "MN"
    elif place == "Manila South C":
        final_place = "MS"
    elif place == "La Loma C":
        final_place = "L"
    elif place == "Manila Chinese C":
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
        messages.error(request, "Please register a profile of your loved one first.")
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
    order.status = "Pa"
    order.save()
    context = {"form": order}
    return render(request, "lapida_app/summary.html", context)


def no_permission(request):
    return render(request, "lapida_app/no_permission.html")


def update_picture(request, id):
    if request.method == "POST":
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


def reserve_task(request, id):
    order = Order_User.objects.get(id=id)
    order_date = datetime.datetime.strftime(order.order_date, "%Y-%m-%d")
    caretaker_profile = CareTaker.objects.get(user=request.user)
    existing_order = Caretaker_Task.objects.filter(caretaker=caretaker_profile)
    order_date_to_be_checked = []
    for x in existing_order:
        if x:
            past_order = x.order
            order_date_to_be_checked.append(
                datetime.datetime.strftime(past_order.order_date, "%Y-%m-%d")
            )
    if order_date in order_date_to_be_checked:
        sweetify.error(
            request,
            "YOU HAVE REACHED YOUR DAILY QUOTA",
            persistent=":(",
        )
        return redirect("summary", order.id)
    else:
        order.status = "P"
        caretaker_task_instance = Caretaker_Task.objects.get(order=order)
        caretaker_task_instance.caretaker = caretaker_profile
        order.save()
        caretaker_task_instance.save()
        User = get_user_model()
        user = User.objects.get(pk=caretaker_profile.user.id)
        user_email = user.email
        current_site = get_current_site(request)
        mail_subject = "New Task"
        message = render_to_string(
            "lapida_app/email_notification.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        to_email = user_email
        send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
        return redirect("summary", order.id)


@receiver(post_save, sender=reserve_task)
def clear_cache(sender, instance, **kwargs):
    cache.clear()
    # call cache clear here


def cancel_request(request, id):
    order = Order_User.objects.get(id=id)
    if order.status == "NT":
        order.delete()
    else:
        order.status = "Ca"
        order.save()
        context = {"form": order}


def export(request):
    member_resource = MasterData_RevisedResource()
    dataset = member_resource.export()
    # response = HttpResponse(dataset.csv, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="member.csv"'
    # response = HttpResponse(dataset.json, content_type='application/json')
    # response['Content-Disposition'] = 'attachment; filename="persons.json"'
    response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="persons.xls"'
    return response


def handle404(request, exception):
    return render(request, "lapida_app/404.html", status=404)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "lapida_app/password_message.html"
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "admin@example.com",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="lapida_app/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


# Create your views here.
