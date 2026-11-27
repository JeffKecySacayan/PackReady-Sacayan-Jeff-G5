from django.contrib import admin

from .models import Category, ListItem, PackingList, Trip, TripType

admin.site.register(TripType)
admin.site.register(Category)
admin.site.register(Trip)
admin.site.register(PackingList)
admin.site.register(ListItem)