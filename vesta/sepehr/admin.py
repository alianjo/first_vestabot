from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Supplier
from .views import AdminTemplate, GetCaptcha, SetCaptcha
from django.urls import path, include
from .forms import CsvImportForm
import csv, json
from io import StringIO
from django.conf.urls import url, include



# admin.site.register(Supplier)

def disable(modeladmin, request, queryset):
    # queryset.update(status=0)
    disabling = AdminTemplate(queryset)
    res = disabling.disableSup()
    if res:
        messages.success(request, "mission complete")
    else:
        messages.error(request, "The mission failed")
disable.short_description = 'Disable selected supplier'

def reload_credit(modeladmin, request, queryset):
    loadCredit = AdminTemplate(queryset)
    res = loadCredit.reloadCreditSup()
    if res:
        messages.success(request, "mission complete")
    else:
        messages.error(request, "The mission failed")
reload_credit.short_description = 'Reload Credit selected supplier'


def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = ['name', 'address', 'username', 'password', 'alias_name']

    response = HttpResponse(content_type='text/csv;')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])
    messages.success(request, "mission complete")
    return response
export_as_csv.short_description = 'Export csv selected supplier'

@admin.register(Supplier)
class SupplierTable(admin.ModelAdmin):
    change_list_template = 'admin/SepehrSupplier.html'
    # change_list_template = '/home/vesta/projects/vestabot/vesta/templates/admin/SepehrSupplier.html'       # definitely not 'admin/change_list.html'
    list_display = ('alias_name', 'name', 'address', 'credit', 'status')  # display these table columns in the list view
    list_filter = ['status']
    ordering = ('alias_name', 'name', 'address', 'credit', 'status')  # sort by most recent subscriber
    # fields = ['name', 'address', 'username', 'password', 'credit', 'state']
    readonly_fields = ['credit', 'status']
    actions = [disable, reload_credit, export_as_csv]
    fieldsets = (
        ('information', {
            'fields': ['name', 'alias_name', 'address', 'username', 'password']
        }),
        ('more information', {
            'classes': ('collapse',),
            'fields': ('credit', 'status'),
        }),
    )

    class Media:
        js = (
            '/static/admin/js/SepehrSupplier.js',  # project static folder
        )


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
            url(r'^GetCaptcha/$', GetCaptcha.as_view(), name="GetCaptchaAPI"),
            url(r'^SetCaptcha/$', SetCaptcha.as_view(), name="SetCaptchaAPI"),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            file = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(StringIO(file), delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    object = Supplier.objects.create(name=row[0], address=row[1],
                                            username=row[2], password=row[3], alias_name=row[4])
                    object.save()
                line_count += 1
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['objects_supplier'] = Supplier.objects.all()
        extra_context['form'] = CsvImportForm()
        return super(SupplierTable, self).changelist_view(request, extra_context=extra_context)

# ------------help----------------

# Admin template
# آدرس های موجود در ادمین تمپلیت در دایرکتوری و فایل زیر در خط 266 قرار دارد
# .venv\lib\python3.5\site-packages\django\contrib\admin\sites.py
#get_urls()