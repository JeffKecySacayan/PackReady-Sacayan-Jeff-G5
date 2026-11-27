from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import ListItemForm, PackingListForm, TripForm
from .models import ListItem, PackingList, Trip

TRAVELER = User.Role.TRAVELER
ADMIN = User.Role.ADMIN


# ---------- Trips ----------

@role_required(TRAVELER)
def trip_list(request):
    trips = (
        Trip.objects.filter(user=request.user)
        .select_related("trip_type")
        .annotate(list_count=Count("packing_lists"))
    )
    return render(request, "packing/trip_list.html", {"trips": trips})


@role_required(TRAVELER)
def trip_create(request):
    form = TripForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            messages.success(request, f"Trip to {trip.destination} created.")
            return redirect("packing:trip_list")
        messages.error(request, "Please fix the errors below.")
    return render(request, "packing/form.html", {
        "form": form,
        "title": "New trip",
        "cancel_url": reverse("packing:trip_list"),
    })


@role_required(TRAVELER)
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    form = TripForm(request.POST or None, instance=trip)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Trip updated.")
            return redirect("packing:trip_list")
        messages.error(request, "Please fix the errors below.")
    return render(request, "packing/form.html", {
        "form": form,
        "title": "Edit trip",
        "cancel_url": reverse("packing:trip_list"),
    })


@role_required(TRAVELER)
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    if request.method == "POST":
        destination = trip.destination
        trip.delete()
        messages.success(request, f"Trip to {destination} deleted.")
        return redirect("packing:trip_list")
    return render(request, "packing/confirm_delete.html", {
        "kind": "trip",
        "object_name": f"{trip.destination} ({trip.start_date})",
        "warning": "Packing lists linked to this trip will be kept but unlinked.",
        "cancel_url": reverse("packing:trip_list"),
    })


# ---------- Packing lists ----------

def _annotated_lists(queryset):
    """Adds item_total and item_packed in one query (avoids slow per-row counts)."""
    return queryset.select_related("trip").annotate(
        item_total=Count("items"),
        item_packed=Count("items", filter=Q(items__is_packed=True)),
    )


@role_required(TRAVELER)
def list_index(request):
    lists = _annotated_lists(PackingList.objects.filter(user=request.user))
    return render(request, "packing/list_index.html", {"lists": lists})


@role_required(TRAVELER)
def list_create(request):
    form = PackingListForm(request.POST or None, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            plist = form.save(commit=False)
            plist.user = request.user
            plist.save()
            messages.success(request, f"List “{plist.name}” created. Add your first items below.")
            return redirect("packing:list_detail", pk=plist.pk)
        messages.error(request, "Please fix the errors below.")
    return render(request, "packing/form.html", {
        "form": form,
        "title": "New packing list",
        "cancel_url": reverse("packing:list_index"),
    })


@role_required(TRAVELER, ADMIN)
def list_detail(request, pk):
    if request.user.role == ADMIN:
        plist = get_object_or_404(PackingList.objects.select_related("user", "trip"), pk=pk)
    else:
        plist = get_object_or_404(
            PackingList.objects.select_related("user", "trip"), pk=pk, user=request.user
        )
    is_owner = plist.user_id == request.user.id

    form = None
    if is_owner:
        form = ListItemForm(request.POST or None, packing_list=plist)
        if request.method == "POST":
            if form.is_valid():
                item = form.save(commit=False)
                item.packing_list = plist
                item.save()
                messages.success(request, f"{item.name} added to the list.")
                return redirect("packing:list_detail", pk=plist.pk)
            messages.error(request, "Could not add the item. Check the errors below.")
    elif request.method == "POST":
        raise PermissionDenied

    items = list(plist.items.select_related("category"))
    total = len(items)
    packed = sum(1 for item in items if item.is_packed)
    percent = round(packed * 100 / total) if total else 0
    return render(request, "packing/list_detail.html", {
        "plist": plist,
        "items": items,
        "total": total,
        "packed": packed,
        "percent": percent,
        "form": form,
        "is_owner": is_owner,
    })


@role_required(TRAVELER)
def list_edit(request, pk):
    plist = get_object_or_404(PackingList, pk=pk, user=request.user)
    form = PackingListForm(request.POST or None, instance=plist, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Packing list updated.")
            return redirect("packing:list_detail", pk=plist.pk)
        messages.error(request, "Please fix the errors below.")
    return render(request, "packing/form.html", {
        "form": form,
        "title": "Edit packing list",
        "cancel_url": reverse("packing:list_detail", args=[plist.pk]),
    })


@role_required(TRAVELER)
def list_delete(request, pk):
    plist = get_object_or_404(PackingList, pk=pk, user=request.user)
    if request.method == "POST":
        name = plist.name
        plist.delete()
        messages.success(request, f"List “{name}” deleted.")
        return redirect("packing:list_index")
    return render(request, "packing/confirm_delete.html", {
        "kind": "packing list",
        "object_name": plist.name,
        "warning": "All items on this list will be deleted too.",
        "cancel_url": reverse("packing:list_detail", args=[plist.pk]),
    })


# ---------- List items ----------

@role_required(TRAVELER)
def item_edit(request, pk):
    item = get_object_or_404(
        ListItem.objects.select_related("packing_list"), pk=pk, packing_list__user=request.user
    )
    form = ListItemForm(request.POST or None, instance=item, packing_list=item.packing_list)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated.")
            return redirect("packing:list_detail", pk=item.packing_list_id)
        messages.error(request, "Please fix the errors below.")
    return render(request, "packing/form.html", {
        "form": form,
        "title": "Edit item",
        "cancel_url": reverse("packing:list_detail", args=[item.packing_list_id]),
    })


@role_required(TRAVELER)
@require_POST
def item_toggle(request, pk):
    item = get_object_or_404(ListItem, pk=pk, packing_list__user=request.user)
    item.is_packed = not item.is_packed
    item.save(update_fields=["is_packed"])
    return redirect("packing:list_detail", pk=item.packing_list_id)


@role_required(TRAVELER)
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(ListItem, pk=pk, packing_list__user=request.user)
    list_pk, name = item.packing_list_id, item.name
    item.delete()
    messages.success(request, f"{name} removed from the list.")
    return redirect("packing:list_detail", pk=list_pk)


# ---------- Admin overview (read-only) ----------

@role_required(ADMIN)
def admin_list_index(request):
    lists = _annotated_lists(PackingList.objects.select_related("user"))
    return render(request, "packing/admin_list_index.html", {"lists": lists})