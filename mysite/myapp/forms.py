from django import forms
from django.core.validators import validate_slug
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from . import models


class SuggestionForm(forms.Form):
    suggestion = forms.CharField(label='Question', widget=forms.Textarea(
        attrs={'maxlength':300, 
        'placeholder':'Write your question here. . . (You can not be delete the question once you submit it.)'}), 
        max_length=300
    )
    category = forms.CharField(label='Category', max_length=20, required=False)
    image = forms.ImageField(label="Image File", required=False)
    image_description = forms.CharField(label='Image Description', max_length=240, required=False)

    def save(self, request, commit=True):
        new_sugg = models.Suggestion(
            suggestion=self.cleaned_data["suggestion"],
            category=self.cleaned_data["category"],
            image=self.cleaned_data["image"],
            image_description=self.cleaned_data["image_description"],
            author=request.user
        )
        if commit:
            new_sugg.save()
        return new_sugg

class CommentForm(forms.Form):
    comment = forms.CharField(label='Answer', 
        widget=forms.Textarea(attrs={"rows":5, 'maxlength':2000, 'placeholder':'Write your answer here. . .'}), max_length=2000)

    def save(self, request, sugg_id, commit=True):
        sugg_instance = models.Suggestion.objects.get(id=sugg_id)
        new_comm = models.Comment(
            suggestion=sugg_instance,
            comment=self.cleaned_data["comment"])
        new_comm.author = request.user
        if commit:
            new_comm.save()
        return new_comm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True
        )

    class Meta:
        model = User
        fields = ("username", "email",
                  "password1", "password2")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class TutorForm(forms.Form):
    education = forms.CharField(label='Education', max_length=100)
    description = forms.CharField(label='Description', 
        widget=forms.Textarea(attrs={"rows":5, 'maxlength':300, 'placeholder':'Introduce yourself, and what you will be tutoring for. . .'}), max_length=300)
    category = forms.CharField(label='Category', max_length=20)
    
    def save(self, request, commit=True):
        new_tutor = models.Tutor(
            education=self.cleaned_data["education"],
            description=self.cleaned_data["description"],
            category=self.cleaned_data["category"],
            author=request.user
        )
        if commit:
            new_tutor.save()
        return new_tutor