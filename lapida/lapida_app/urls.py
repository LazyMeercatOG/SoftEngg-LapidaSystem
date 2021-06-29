from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin
from django.conf.urls import handler404


urlpatterns = [
    path("", views.index, name="home-view"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("register/", views.register, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register_dead/", views.create_dead, name="create-dead"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("menu/", views.menu, name="menu"),
    path("summary/<int:id>", views.summary, name="summary"),
    path("update_picture/<int:id>", views.update_picture, name="update-picture"),
    path("success/<int:id>", views.approve_payment, name="approvepayment"),
    path("update_status/<int:id>", views.update_status, name="update-status"),
    path("reserve_task/<int:id>", views.reserve_task, name="reserved-status"),
    path("cancel_request/<int:id>", views.cancel_request, name="cancel-status"),
    path("delete/<slug:uid>", views.delete_record, name="delete"),
    path("403/", views.no_permission, name="404"),
    path("admin/", admin.site.urls),
    url(r"^export-exl/$", views.export, name="export"),
    url(r"^export-csv/$", views.export, name="export"),
    # path("account/", include("django.contrib.auth.urls")),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="lapida_app/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="lapida_app/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="lapida_app/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("password_reset", views.password_reset_request, name="password_reset"),
]
