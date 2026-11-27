from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from packing.models import PackingList, Trip

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("accounts:login")
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse("accounts:dashboard")

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name or user.username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


@login_required
def dashboard_redirect(request):
    if request.user.role == User.Role.ADMIN:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:traveler_dashboard")


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    recent_lists = (
        PackingList.objects.select_related("user", "trip")
        .annotate(
            item_total=Count("items"),
            item_packed=Count("items", filter=Q(items__is_packed=True)),
        )[:5]
    )
    context = {
        "total_users": User.objects.count(),
        "total_travelers": User.objects.filter(role=User.Role.TRAVELER).count(),
        "total_trips": Trip.objects.count(),
        "total_lists": PackingList.objects.count(),
        "recent_lists": recent_lists,
    }
    return render(request, "accounts/admin_dashboard.html", context)


@role_required(User.Role.TRAVELER)
def traveler_dashboard(request):
    my_lists = PackingList.objects.filter(user=request.user)
    recent_lists = (
        my_lists.select_related("trip")
        .annotate(
            item_total=Count("items"),
            item_packed=Count("items", filter=Q(items__is_packed=True)),
        )[:5]
    )
    upcoming_trips = Trip.objects.filter(
        user=request.user, end_date__gte=timezone.localdate()
    ).select_related("trip_type")[:5]
    context = {
        "trip_count": Trip.objects.filter(user=request.user).count(),
        "list_count": my_lists.count(),
        "recent_lists": recent_lists,
        "upcoming_trips": upcoming_trips,
    }
    return render(request, "accounts/traveler_dashboard.html", context)


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile": request.user})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        messages.error(request, "Could not update your profile. Check the errors below.")
    return render(request, "accounts/profile_edit.html", {"form": form})