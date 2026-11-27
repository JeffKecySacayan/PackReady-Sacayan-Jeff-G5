from django.urls import path

from . import views

app_name = "packing"

urlpatterns = [
    path("trips/", views.trip_list, name="trip_list"),
    path("trips/new/", views.trip_create, name="trip_create"),
    path("trips/<int:pk>/edit/", views.trip_edit, name="trip_edit"),
    path("trips/<int:pk>/delete/", views.trip_delete, name="trip_delete"),
    path("lists/", views.list_index, name="list_index"),
    path("lists/new/", views.list_create, name="list_create"),
    path("lists/<int:pk>/", views.list_detail, name="list_detail"),
    path("lists/<int:pk>/edit/", views.list_edit, name="list_edit"),
    path("lists/<int:pk>/delete/", views.list_delete, name="list_delete"),
    path("items/<int:pk>/edit/", views.item_edit, name="item_edit"),
    path("items/<int:pk>/toggle/", views.item_toggle, name="item_toggle"),
    path("items/<int:pk>/delete/", views.item_delete, name="item_delete"),
    path("manage/lists/", views.admin_list_index, name="admin_list_index"),
]