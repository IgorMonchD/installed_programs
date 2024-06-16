from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

admin.site.register(ProgramData)
admin.site.register(Installation)
admin.site.register(Host)

class OriginAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(Origin, OriginAdmin)

class TypicalActivityAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(TypicalActivity, TypicalActivityAdmin)

class TagAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(Tag, TagAdmin)

class InspectionAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(Inspection, InspectionAdmin)

class DirectoryAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(Directory, DirectoryAdmin)

class ProgramCategoryAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(ProgramCategory, ProgramCategoryAdmin)

class ProgramClassAdmin(ImportExportModelAdmin):
    exclude = ('id',)

admin.site.register(ProgramClass, ProgramClassAdmin)
