from django import forms

from accounts.forms import BootstrapFormMixin

from .models import ListItem, PackingList, Trip


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(**kwargs)


class TripForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Trip
        fields = ("destination", "trip_type", "start_date", "end_date")
        widgets = {"start_date": DateInput(), "end_date": DateInput()}

    def clean_destination(self):
        return self.cleaned_data["destination"].strip()

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before the start date.")
        return cleaned


class PackingListForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PackingList
        fields = ("name", "trip")

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["trip"].queryset = Trip.objects.filter(user=user)
        self.fields["trip"].empty_label = "No trip yet"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = PackingList.objects.filter(user=self.user, name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("You already have a packing list with this name.")
        return name


class ListItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ("name", "quantity", "category")

    def __init__(self, *args, packing_list, **kwargs):
        super().__init__(*args, **kwargs)
        self.packing_list = packing_list
        self.fields["category"].empty_label = "No category"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = ListItem.objects.filter(packing_list=self.packing_list, name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("This item is already on the list. Edit its quantity instead.")
        return name

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > 99:
            raise forms.ValidationError("Quantity cannot be more than 99.")
        return quantity