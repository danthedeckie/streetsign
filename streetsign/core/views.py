from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify


from .models import Feed
from .forms import NewFeedForm

# Create your views here.

def feeds_list(request):
    feeds = Feed.objects.all()

    if request.method == 'POST':
        form = NewFeedForm(request.POST)
        if form.is_valid():
            feed = Feed(name=form.cleaned_data['name'])
            feed.slug = slugify(feed.name)
            feed.save()
            return redirect(feed.get_absolute_url())
    else:
        form = NewFeedForm()

    return render(request, 'feeds_list.html', context={
        "feeds": feeds,
        "newfeedform": form,
        })

def feed_view(request, slug):
    feed = get_object_or_404(Feed, slug=slug)

    return render(request, 'feed_view.html', context={
        "feed": feed
        })
