from django import forms
from .models import Topic

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['Title', 'Content','Category', 'Date', 'Time', 'Author']