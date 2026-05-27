from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import ItemReport

class CustomUserCreationForm(UserCreationForm):
    """Refined signup form restricted to high-confidence credentials and email-only verification."""
    email = forms.EmailField(required=True, help_text=_("Required for communication and recovery notifications."))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ItemReportForm(forms.ModelForm):
    """Standardized report form optimized for precision geospatial data capture."""
    location_name = forms.CharField(widget=forms.TextInput(attrs={
        'id': 'id_location_name', 
        'placeholder': _('Location description or select on map')
    }), label=_('Location Name'))
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False, label=_('Latitude'))
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False, label=_('Longitude'))
    accuracy = forms.FloatField(widget=forms.HiddenInput(), required=False, label=_('Accuracy'))
    item_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label=_('Item Date'))
    
    class Meta:
        model = ItemReport
        fields = [
            'report_type', 'category', 'title', 'description', 
            'location_name', 'latitude', 'longitude', 'accuracy', 
            'item_date', 'contact_info', 'photo'
        ]
