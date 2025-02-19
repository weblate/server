from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class UserStampedModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


class AcceptRejectModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.model_name = model.__name__
        super().__init__(model, admin_site)

    def response_change(self, request, obj):
        if "_reject" in request.POST:
            obj.status = "rejected"
            obj.save()
            self.message_user(
                request, _("{name} rejected").format(name=self.model_name)
            )
            return HttpResponseRedirect(".")
        if "_accept" in request.POST:
            obj.status = "accepted"
            obj.save()
            self.message_user(
                request, _("{name} accepted").format(name=self.model_name)
            )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
