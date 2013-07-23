# -*- coding: utf-8 -*-
"""  Concertino Digital Signage Project : LOGIC (feeds and posts)
     (C) Copyright 2013 Daniel Fairhead

    Concertino is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Concertino is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Concertino.  If not, see <http://www.gnu.org/licenses/>.

    -----------------------------------------------------------

    logic for feeds_and_posts views, separated out for clarity.

"""

from flask import flash, url_for, json
from app.views.utils import PleaseRedirect
from app.models import Post, Feed
from datetime import datetime

def try_to_set_feed(post, form, user):
    ''' Is this user actually allowed to set the feed of this post to what
        the form is saying they want to?  If so, cool. Return that feed. '''

    try:
        if post.feed:
            oldfeedid = post.feed.id
        else:
            oldfeedid = False
    except:
        oldfeedid = False

    if form.get('post_feed', oldfeedid) != oldfeedid:
        # new or changed feed.
        try:
            feed = Feed.get(Feed.id==form.get('post_feed'))
        except Feed.DoesNotExist:
            raise PleaseRedirect(None,
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

        raise PleaseRedirect(None,
            "Sorry, this post is in feed '{0}', which"
            " you don't have permission to post to."
            " Edit cancelled.".format(post.feed.name))

    # if this post is already published, be careful about editing it!
    if post.published and not post.feed.user_can_publish(user):

        raise PleaseRedirect(None,
            'Sorry, this post is published, and you do not have'
            'permission to edit published posts in "{0}".'.format(post.feed.name))

    return True

def can_user_write_and_publish(user, post):
    if not post.feed:
        if user.writeable_feeds():
            return True, False

    else: # there is a feed selected
        if post.feed.user_can_write(user):
            if post.feed.user_can_publish(user):
                return True, True
            else:
                return True, False

    # default is secure:
    return False, False

def post_form_intake(post, form, editor):

    # note! this actually modifies the post it is sent!
    content=json.dumps(editor.receive(form))
    post.content = content

    try:
        post.active_start = datetime.strptime(form.get("active_start"), '%Y-%m-%d %H:%M')
        post.active_end = datetime.strptime(form.get("active_end"), '%Y-%m-%d %H:%M')
    except:
        flash('Problem with date.')

    post.time_restrictions_show = (form.get('times_mode', \
                'do_not_show') \
            == 'only_show')
    post.time_restrictions = form.get('time_restrictions_json','[]')
    post.display_time = min(100, max(2, int(form.get('displaytime'))))

