# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
#     (C) Copyright 2013 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
#    -------------------------------
"""
---------------------------------------
streetsign_server.logic.feeds_and_posts
---------------------------------------

logic for feeds_and_posts views, separated out for clarity.

"""

from datetime import datetime

from flask import flash, url_for, json

from streetsign_server.views.utils import PleaseRedirect, \
                                          getstr, getint, getbool, \
                                          STRIPSTR, DATESTR
from streetsign_server.models import Feed, now

def try_to_set_feed(post, new_feed_id, user):
    ''' Is this user actually allowed to set the feed of this post to what
        the form is saying they want to?  If so, cool. Return that feed. '''

    try:
        if post.feed:
            oldfeedid = post.feed.id
        else:
            oldfeedid = False
    except:
        oldfeedid = False

    if new_feed_id and new_feed_id != oldfeedid:
        # new or changed feed.
        try:
            feed = Feed.get(Feed.id == new_feed_id)
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
            raise PleaseRedirect(
                url_for('index'),
                "Sorry, you don't have permission to write to " + feed.name)
        return feed

    return post.feed

def if_i_cant_write_then_i_quit(post, user):
    ''' checks if a post is editable by a user. If it isn't, for
        whatever reason, then raise an appropriate 'PleaseRedirect'
        exception. (reasons could be that it's in a feed we don't
        have write access to, or it's been published, and we don't
        have publish permission to that feed, so the post is now
        'locked' to us.) '''

    # if we don't have write permission, then this isn't our post!
    if not post.feed.user_can_write(user):

        raise PleaseRedirect(
            None,
            "Sorry, this post is in feed '{0}', which"
            " you don't have permission to post to."
            " Edit cancelled.".format(post.feed.name))

    # if this post is already published, be careful about editing it!
    if post.published and not post.feed.user_can_publish(user):

        raise PleaseRedirect(
            None,
            'Sorry, this post is published,'
            ' and you do not have permission to'
            ' edit published posts in "{0}".'.format(post.feed.name))

    return True

def can_user_write_and_publish(user, post):
    ''' returns a tuple, expressing if 'user' has permission to
        write and publish a post. '''

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

def clean_date(in_text):
    ''' take some input text, and return a datetime, if possible. '''
    return datetime.strptime(in_text.split('.')[0], "%Y-%m-%d %H:%M:%S")

def post_form_intake(post, form, editor):
    ''' takes the values from 'form', passes the post contents to
        the editor 'receive' function, and adds all the values into
        the 'post' object.

        NOTE: this actually modifies the post it is sent!
    '''

    post.content = json.dumps(editor.receive(form))

    post.status = 0 # any time a post is edited, remove it from archive.

    post.time_restrictions_show = \
        (form.get('times_mode', 'do_not_show') == 'only_show')
    post.time_restrictions = form.get('time_restrictions_json', '[]')
    post.display_time = \
        getint('displaytime', 8, minimum=2, maximum=100, form=form)

    print type(form['active_start'])

    post.active_start = \
        getstr('active_start', post.active_start, validate=DATESTR, form=form)

    print type(post.active_start)
    post.active_end = \
        getstr('active_end', post.active_end, validate=DATESTR, form=form)

    post.write_date = now()

def delete_post_and_run_callback(post, typemodule):
    ''' before a post is actually deleted, check if there is a 'pre-delete'
        callback on this post type, and run that first.  This way, for uploaded
        images (for instance), the file can be deleted as well. '''

    try:
        typemodule.delete(json.loads(post.content))
    except AttributeError as excp:
        pass
        # There's no callback for this posttype, which is fine.
        # most post types will store no external data, and so don't need
        # to do anything.
    except Exception as excp:
        flash(str(excp))

    return post.delete_instance()
