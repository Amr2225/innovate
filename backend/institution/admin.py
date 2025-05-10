from django.contrib import admin

from institution.models import Plan, Payment, Offer

admin.site.register(Plan)
admin.site.register(Payment)
admin.site.register(Offer)

# Register your models here.
