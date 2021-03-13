from django.contrib import admin
from .models import (
    Profile,
    User_Place,
    MasterData_Revised,
    CareTaker,
    Order_User,
    Caretaker_Task,
)
from import_export.admin import ImportExportModelAdmin


admin.site.register(Profile)
admin.site.register(User_Place)
admin.site.register(CareTaker)
admin.site.register(Order_User)
admin.site.register(Caretaker_Task)


@admin.register(MasterData_Revised)
class MasterData_Revised_Admin(ImportExportModelAdmin):
    list_display = (
        "uid",
        "place",
        "last_name",
        "first_name",
        "middle_name",
        "birthdate",
        "category",
        "blk",
        "street",
        "lot",
    )
    pass


# Register your models here.
