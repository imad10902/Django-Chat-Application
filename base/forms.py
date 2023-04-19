from django.forms import ModelForm
from .models import Room

#creating form with metadeta from Room model
#to tell it is form we are dealing with
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
    