from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class TripType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Trip(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips"
    )
    trip_type = models.ForeignKey(TripType, on_delete=models.PROTECT, related_name="trips")
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before the start date.")

    def __str__(self):
        return f"{self.destination} ({self.start_date})"


class PackingList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="packing_lists"
    )
    trip = models.ForeignKey(
        Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name="packing_lists"
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_items(self):
        return self.items.count()

    @property
    def packed_items(self):
        return self.items.filter(is_packed=True).count()

    @property
    def progress_percent(self):
        total = self.total_items
        return round(self.packed_items * 100 / total) if total else 0

    def __str__(self):
        return self.name


class ListItem(models.Model):
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_packed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_packed", "name"]

    def __str__(self):
        return f"{self.name} x{self.quantity}"