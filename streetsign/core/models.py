from django.db import models

# Create your models here.

class User(Ab

class Feed(models.Model):
    name = models.CharField(max_length=100, allow_unicode=True, default='New Feed')
    slug = models.SlugField(max_length=100, allow_unicode=True)

class Post(models.Model):
    contenttype = models.SlugField(max_length=100, allow_unicode=True, default='plaintext')
    
    content_json = models.TextField(default='{}', blank=True)

    feed = models.ForeignKeyField(Feed,
                                  on_delete=models.CASCADE,
                                  related_name='posts_all')

