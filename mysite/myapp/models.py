from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Suggestion(models.Model):
    suggestion = models.TextField(max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        max_length=144, upload_to='uploads/%Y/%m/%d/')
    image_description = models.CharField(max_length=240)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.author.username + " " + self.suggestion

class Comment(models.Model):
    comment = models.CharField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)

    def __str__(self):
        return self.author.username + " " + self.comment

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(blank=True, null=True, max_length=225)
    status = models.CharField(blank=True, null=True, max_length=225)
    created_at = models.DateTimeField(auto_now=True)

class Tutor(models.Model):
    education = models.TextField(max_length=100)
    description = models.TextField(max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.author.username + " " + self.description