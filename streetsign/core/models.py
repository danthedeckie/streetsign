from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from model_utils.models import TimeStampedModel, TimeFramedModel
from model_utils import Choices

from users.models import User

class Feed(models.Model):
    name = models.CharField(max_length=100, default='New Feed')
    slug = models.SlugField(max_length=100, allow_unicode=True)

    authors = models.ManyToManyField(User, related_name='writable_feeds')
    publishers = models.ManyToManyField(User, related_name='publishable_feeds')

    def posts_active(self):
        return self.posts_all.filter(status=Post.STATUS.active)

    def get_absolute_url(self):
        return reverse('feed-view', args=(self.slug,))

class Post(models.Model):
    STATUS = Choices(
                ('draft', _('Draft')),
                ('active', _('Active')),
                ('archived', _('Archived')),
                ('deleted', _('Deleted')),
            )
    status = models.CharField(max_length=16, default=STATUS.draft)
    ctime = models.DateTimeField(auto_now_add=True, editable=False)
    mtime = models.DateTimeField(auto_now=True, editable=False)


    contenttype = models.SlugField(max_length=100, allow_unicode=True, default='plaintext')

    content_json = models.TextField(default='{}', blank=True)
    author = User

    feed = models.ForeignKey(
            Feed,
            on_delete=models.CASCADE,
            related_name='posts_all')

    def get_absolute_url(self):
        return reverse('post-view', args=[self.id])
