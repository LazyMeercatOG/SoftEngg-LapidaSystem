from django.contrib import admin
from .models import Profile, User_Place, MasterData_Revised
from import_export.admin import ImportExportModelAdmin


admin.site.register(Profile)
admin.site.register(User_Place)
@admin.register(MasterData_Revised)
class MasterData_Revised_Admin(ImportExportModelAdmin):
    list_display = ("uid","place", "last_name", "first_name", "middle_name", "category", "blk", "street", "lot")
    pass 
# Register your models here.
