'''
    logic for feeds_and_posts views, separated out for clarity.

'''

from flask import flash
from app.views.utils import PleaseRedirect
from app.models import Post, Feed

def try_to_set_feed(post, form, user):
    ''' Is this user actually allowed to set the feed of this post to what
        the form is saying they want to?  If so, cool. Return that feed. '''

    if not post.feed and 'feedid' in form and form.get('feedid')!=post.feed.id:
        # new or changed feed.
        try:
            feed = Feed.get(Feed.id==request.form.get('feedid'))
        except Feed.DoesNotExist:
            raise PleaseRedirect(url_for('postpage',postid=postid),
                  "Odd. You somehow tried to post "
                  "to a non-existant feed. It didn't work.")

        if feed.user_can_write(user):
            flash('Posted to ' + feed.name)
            return feed

        else:
            # This shouldn't happen very often - so don't worry about
            # losing post data.  If it's an issue, refactor so it's stored
            # but not written to the feed...
            raise PleaseRedirect(url_for('index'),
                "Sorry, you don't have permission to write to " + feed.name)
        return feed

    return post.feed

def if_i_cant_write_then_i_quit(post, user):
    # if we don't have write permission, then this isn't our post!
    if not post.feed.user_can_write(user):

        raise PleaseRedirect(url_for('postpage', postid=postid),
            "Sorry, this post is in feed '{0}', which"
            " you don't have permission to post to."
            " Edit cancelled.".format(post.feed.name))

    # if this post is already published, be careful about editing it!
    if post.published and not post.feed.user_can_publish(user):

        raise PleaseRedirect( url_for('postpage', postid=postid),
            'Sorry, this post is published, and you do not have'
            'permission to edit published posts in "{0}".'.format(f.name))

    return True

def can_user_write_and_publish(user, post):
    if not post.feed:
        if user.writable_feeds():
            return True, False

    else: # there is a feed selected
        if post.feed.user_can_write(user):
            if post.feed.user_can_publish(user):
                return True, True
            else:
                return True, False

    # default is secure:
    return False, False
