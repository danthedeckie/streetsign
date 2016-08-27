# -*- coding: utf-8 -*-
#     StreetSign Digital Signage Project
#     (C) Copyright 2013-2015 Daniel Fairhead
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
#    ---------------------------------

"""
    streetsign_server.views.feeds_and_posts
    ---------------------------------------
    Views for editing feeds and posts.

"""

# alas, due to peewee:
#pylint: disable=no-value-for-parameter,unexpected-keyword-arg

from datetime import timedelta

from flask import render_template, url_for, request, redirect, \
                  flash, json, jsonify, make_response
import peewee
from feedformatter import Feed as RSSFeed
import bleach

import streetsign_server.user_session as user_session
import streetsign_server.post_types as post_types
from streetsign_server.views.utils import PleaseRedirect, getint, getbool, \
                                          getstr, DATESTR, \
                                          admin_only, \
                                          registered_users_only

from streetsign_server.logic.feeds_and_posts import try_to_set_feed, \
                                      if_i_cant_write_then_i_quit, \
                                      can_user_write_and_publish, \
                                      post_form_intake, \
                                      delete_post_and_run_callback

from streetsign_server import app
from streetsign_server.models import User, Group, Feed, Post, ExternalSource, \
                                     by_id, config_var, PermissionDenied, \
                                     now

import streetsign_server.external_source_types as external_source_types

####################################################################
# Feeds & Posts:

@app.route('/feeds/', methods=['GET', 'POST'])
@admin_only('POST')
@registered_users_only('GET')
def feeds():
    ''' the back end list of feeds. '''

    if request.method == 'POST':
        action = request.form.get('action', 'create')

        if action == 'create':
            if not request.form.get('title', '').strip():
                flash("I'm not making you an un-named feed!")
                return redirect(url_for('feeds'))
            Feed(name=request.form.get('title', 'blank').strip()).save()

    try:
        user = user_session.get_user()
    except user_session.NotLoggedIn:
        user = User()

    return render_template('feeds.html',
                           feeds=Feed.select(),
                           user=user,
                           external_sources=ExternalSource.select(),
                           source_types=external_source_types.types())

@app.route('/feeds/<int:feedid>', methods=['GET', 'POST'])
def feedpage(feedid):
    ''' the back end settings for one feed. '''

    try:
        feed = Feed.get(id=feedid)
        user = user_session.get_user()
    except user_session.NotLoggedIn:
        user = User()
    except:
        flash('invalid feed id! (' + str(feedid) + ')')
        return redirect(url_for('feeds'))

    if request.method == 'POST':
        if not user_session.logged_in():
            flash("You're not logged in!")
            return redirect(url_for('feeds'))

        if not user.is_admin:
            flash('Sorry! Only Admins can change these details.')
            return redirect(request.referrer)

        action = request.form.get('action', 'none')

        if action == 'edit':
            feed.name = request.form.get('title', feed.name).strip()

            inlist = request.form.getlist

            feed.post_types = ', '.join(inlist('post_types'))

            feed.set_authors(by_id(User, inlist('authors')))
            feed.set_publishers(by_id(User, inlist('publishers')))
            feed.set_author_groups(by_id(Group, inlist('author_groups')))
            feed.set_publisher_groups(by_id(Group, inlist('publisher_groups')))

            feed.save()
            flash('Saved')
        elif action == 'delete':

            for post in feed.posts:
                post_type_module = post_types.load(post.type)
                delete_post_and_run_callback(post, post_type_module)

            feed.delete_instance(True, True) # cascade/recursive delete.
            flash('Deleted')
            return redirect(url_for('feeds'))

    return render_template('feed.html',
                           feed=feed,
                           user=user,
                           all_posttypes=post_types.types(),
                           allusers=User.select(),
                           allgroups=Group.select()
                          )


@app.route('/feeds/rss/<ids_raw>')
def feedsrss(ids_raw):
    ''' get a bunch of feeds posts as an RSS stream '''

    ids = []
    feed_names = []

    for i in ids_raw.split(','):
        try:
            feedid = int(i)
            if feedid in ids:
                continue

            feed = Feed.get(id=feedid)
            ids.append(feedid)
            feed_names.append(feed.name)
        except ValueError:
            continue
        except Feed.DoesNotExist:
            continue

    time_now = now()
    feed_posts = [p for p in \
                  Post.select().join(Feed).where(
                      (Feed.id << ids)
                      &(Post.status == 0)
                      &(Post.active_start < time_now)
                      &(Post.active_end > time_now)
                      &(Post.published)
                      )]

    feed = RSSFeed()

    feed.feed["title"] = ",".join(feed_names)
    feed.feed["link"] = url_for('feeds')
    feed.feed["description"] = "Posts from " + (','.join(feed_names))

    for post in feed_posts:
        contents = json.loads(post.content)
        cleantext = bleach.clean(contents["content"], tags=[], strip=True)
        if len(cleantext) > 20:
            cleantext = cleantext[0:20] + "..."

        item = {
            "title": cleantext,
            "description": contents["content"],
            "guid": str(post.id),

            }
        feed.items.append(item)

    resp = make_response(feed.format_rss2_string())
    resp.headers["Content-Type"] = "application/xml"

    return resp



##########################################
# Posts:

@app.route('/posts/')
@admin_only('POST')
@registered_users_only('GET')
def posts():
    ''' (HTML) list of ALL posts. (also deletes broken posts, if error) '''

    try:
        user = user_session.get_user()
    except user_session.NotLoggedIn:
        user = User()

    try:
        if user.is_admin:
            return render_template('posts.html', posts=Post.select(), user=user)
        else:
            return render_template('posts.html',
                                   posts=Post.select() \
                                             .where(Post.status == 0), user=user)
    except Feed.DoesNotExist:
        # Ah. Database inconsistancy! Not good, lah.
        ps = Post.raw('select post.id from post'
                      ' left join feed on feed.id = post.feed_id'
                      ' where feed.id is null;')
        for p in ps:
            p.delete_instance()
        flash('Cleaned up old posts...')

    if user.is_admin:
        return render_template('posts.html', posts=Post.select(), user=user)
    else:
        return render_template('posts.html',
                               posts=Post.select()\
                                         .where(Post.status == 0), user=user)

@registered_users_only('GET', 'POST')
@app.route('/posts/new/<int:feed_id>', methods=['GET', 'POST'])
def post_new(feed_id):
    ''' create a new post! '''

    #if not user_session.logged_in():
    #    flash("You're not logged in!")
    #    return redirect(url_for('index'))

    user = user_session.get_user()

    try:
        feed = Feed.get(id=feed_id)
    except Feed.DoesNotExist:
        flash('Sorry, Feed does not exist!')
        return redirect(url_for('feeds'))

    if not feed.user_can_write(user):
        flash("Sorry! You don't have permission to write here!")
        return redirect(request.referrer if request.referrer else '/')

    if request.method == 'GET':
        # send a blank form for the user:

        post = Post()
        post.feed = feed

        # give list of available post types:

        all_posttypes = dict([(x['id'], x) for x in post_types.types()])

        if post.feed.post_types:

            allowed_post_types = []

            for post_type in post.feed.post_types_as_list():
                if post_type in all_posttypes:
                    allowed_post_types.append(all_posttypes[post_type])
        else:
            allowed_post_types = all_posttypes.values()

        # return the page:

        return render_template('postnew.html',
                               current_feed=feed,
                               post=post,
                               user=user,
                               post_types=allowed_post_types)

    else: # POST. new post!
        post_type = request.form.get('post_type')
        try:
            post_type_module = post_types.load(post_type)
        except:
            flash('Sorry! invalid post type.')
            return redirect(request.referrer if request.referrer else '/')

        if feed.post_types and post_type not in feed.post_types_as_list():
            flash('sorry! this post type is not allowed in this feed!')
            return redirect(request.referrer if request.referrer else '/')

        post = Post(type=post_type, author=user)

        try:
            post.feed = feed

            if_i_cant_write_then_i_quit(post, user)

            post_form_intake(post, request.form, post_type_module)

        except PleaseRedirect as e:
            flash(str(e.msg))
            return redirect(e.url if e.url else request.url)

        post.save()
        flash('Saved!')

        return redirect(url_for('feedpage', feedid=post.feed.id))

@app.route('/posts/<int:postid>', methods=['GET', 'POST'])
def postpage(postid):
    ''' Edit a post. '''

    if not user_session.logged_in():
        flash("You're not logged in!")
        return redirect(url_for('posts'))

    try:
        post = Post.get(Post.id == postid)
        post_type_module = post_types.load(post.type)
        user = user_session.get_user()

    except Post.DoesNotExist:
        flash('Sorry! Post id:{0} not found!'.format(postid))
        return redirect(url_for('posts'))

    if request.method == 'POST':
        try:
            # check for write permission, and if the post is
            # already published, publish permission.

            if_i_cant_write_then_i_quit(post, user)

            # if the user is allowed to set the feed to what they've
            # requested, then do it.

            post.feed = try_to_set_feed(post,
                                        request.form.get('post_feed', False),
                                        user)

        except PleaseRedirect as e:
            flash(str(e.msg))
            redirect(e.url)

        # if it's a publish or delete request, handle that instead:
        action = request.form.get('action', 'edit')

        if action == 'delete':
            # don't need extra guards, as if_i_cant... deals with it above
            delete_post_and_run_callback(post, post_type_module)
            flash('Deleted')
        elif action == 'publish':
            try:
                post.publish(user)
                flash("Published")
            except PermissionDenied:
                flash("Sorry, you don't have permission to publish"
                      " posts in this feed.")
        elif action == 'unpublish':
            try:
                post.publish(user, False)
                flash("Published!")
            except PermissionDenied:
                flash('Sorry, you do NOT have permission' \
                       ' to unpublish on this feed.')
        elif action == 'move':
            if not user_session.is_admin():
                flash('Sorry! You are not an admin!')
                return jsonify({'error': 'permission denied'})
            post.feed = Feed.get(Feed.id == getint('feed', post.feed))
            post.save()
            return jsonify({'message': 'Moved to ' + post.feed.name})

        if action not in ('edit', 'update'):
            return redirect(request.referrer if request.referrer else '/')

        # finally get around to editing the content of the post...
        try:
            post_form_intake(post, request.form, post_type_module)
            post.save()
            flash('Updated.')
        except Exception as e:
            flash('invalid content for this data type!')
            flash(str(e))

    # Should we bother displaying 'Post' button, and editable controls
    # if the user can't write to this post anyway?

    #can_write, can_publish = can_user_write_and_publish(user, post)

    return render_template('post_editor.html',
                           post=post,
                           current_feed=post.feed.id,
                           feedlist=user.writeable_feeds(),
                           user=user,
                           form_content=post_type_module.form(json.loads(post.content)))

@app.route('/posts/edittype/<typeid>')
def postedit_type(typeid):
    ''' returns an editor page, of type typeid '''

    post_type_module = post_types.load(typeid)

    return render_template('post_type_container.html',
                           post_type=typeid,
                           form_content=post_type_module.form(request.form))


@app.route('/posts/housekeeping', methods=['POST'])
def posts_housekeeping():
    ''' goes through all posts, move 'old' posts to archive status,
        delete reeeeealy old posts. '''

    time_now = now()
    archive_time = time_now - \
                   timedelta(days=config_var('posts.archive_after_days', 7))
    delete_time = time_now - \
                  timedelta(days=config_var('posts.delete_after_days', 30))

    # first delete really old posts:

    delete_count = 0
    archive_count = 0

    if config_var('posts.delete_when_old', True):
        for post in Post.select().where(Post.active_end < delete_time):
            delete_post_and_run_callback(post, post_types.load(post.type))
            delete_count += 1

    # next set old-ish posts to archived:

    if config_var('posts.archive_when_old', True):
        archive_count = Post.update(status=2) \
                            .where((Post.active_end < archive_time) &
                                   (Post.status != 2)) \
                            .execute()

    # And done.

    return jsonify({"deleted": delete_count,
                    "archived": archive_count,
                    "delete_before": delete_time,
                    "archive_before": archive_time,
                    "now": time_now})

###############################################################

@app.route('/posts/<int:postid>/json')
def json_post(postid):
    try:
        return jsonify(Post.get(Post.id == postid).dict_repr())
    except:
        return jsonify({"error": "Invalid Post ID"})

###############################################################

@app.route('/external_data_sources/NEW',
           defaults={'source_id': None},
           methods=['GET', 'POST'])
@app.route('/external_data_sources/<int:source_id>',
           methods=['GET', 'POST', 'DELETE'])
def external_data_source_edit(source_id):
    ''' Editing a external data source '''

    if not user_session.is_admin():
        flash('Only Admins can do this!')
        return redirect(url_for('feeds'))

    # first find the data type:

    if request.method == 'DELETE':
        ExternalSource.delete() \
                      .where(ExternalSource.id == int(source_id)) \
                      .execute()
        return 'deleted'

    if source_id == None:
        try:
            source = ExternalSource()
            source.type = request.args['type']
            source.name = "new " + source.type + " source"
            source.feed = Feed.get() # set initial feed
        except KeyError:
            return 'No type specified.', 500
    else:
        try:
            source = ExternalSource.get(id=source_id)
        except peewee.DoesNotExist:
            return 'Invalid id.', 404

    # Try and load the external source type ( and check it's valid):

    try:
        module = external_source_types.load(source.type)
    except ImportError:
        return 'Invalid External Source Type', 404

    # if it's a post, then update the data with 'receive':

    if request.method == 'POST':
        source.post_as_user = user_session.get_user()

        source.settings = json.dumps(module.receive(request))
        source.name = request.form.get('name', source.name)

        source.frequency = getint('frequency', 60)
        source.publish = getbool('publish', False)
        source.lifetime_start = getstr('active_start',
                                       source.lifetime_start,
                                       validate=DATESTR)
        source.lifetime_end = getstr('active_end',
                                     source.lifetime_end,
                                     validate=DATESTR)
        source.display_time = getint('display_time', source.display_time)
        source.post_template = request.form.get('post_template',
                                                source.post_template)
        try:
            source.feed = Feed.get(Feed.id == getint('feed', 100))
            source.save()
            if source_id == None:
                # new source!
                return redirect(url_for('external_data_source_edit',
                                        source_id=source.id))
            else:
                flash('Updated.')
        except Feed.DoesNotExist:
            flash("Can't save! Invalid Feed!{}".format(
                getint('feed', '-11')))


    return render_template("external_source.html",
                           source=source,
                           feeds=Feed.select(),
                           form=module.form(json.loads(source.settings)))


@app.route('/external_data_sources/test')
def external_source_test():
    '''
        test an external source, and return some comforting HTML
        (for the editor)
    '''
    if not user_session.is_admin():
        flash('Only Admins can do this!')
        return redirect(url_for('feeds'))

    '''
    try:
        source = ExternalSource.get(id=source_id)
    except ExternalSource.DoesNotExist:
        return 'Invalid Source.', 404
    '''
    # load the type module:
    module = external_source_types.load(request.args.get('type', None))
    # and request the test html
    return module.test(request.args)

@app.route('/external_data_sources/<int:source_id>/run', methods=['POST'])
def external_source_run(source_id):
    ''' use the importer specified to see if there is any new data,
        and if there is, then import it. '''

    try:
        source = ExternalSource.get(id=source_id)
    except ExternalSource.DoesNotExist:
        return 'Invalid Source', 404

    time_now = now()
    if user_session.is_admin() and request.form.get('force', 'no') == 'yes':
        flash("Update forced.")
    else:
        if source.last_checked:
            next_check = source.last_checked + timedelta(minutes=source.frequency)

            if next_check > time_now:
                return "Nothing to do. Last: {0}, Next: {1}, Now: {2} ".format(
                    source.last_checked, next_check, time_now)

    module = external_source_types.load(source.type)

    settings_data = json.loads(source.settings)
    new_posts = module.get_new(settings_data)

    if new_posts:
        for fresh_data in new_posts:
            post = Post(type=fresh_data.get('type', 'html'), \
                        author=source.post_as_user)
            post_type_module = post_types.load(fresh_data.get('type', 'html'))

            post.feed = source.feed

            fresh_data['active_start'] = source.current_lifetime_start()
            fresh_data['active_end'] = source.current_lifetime_end()

            post_form_intake(post, fresh_data, post_type_module)
            post.display_time = source.display_time

            if source.publish:
                post.publisher = source.post_as_user
                post.publish_date = now()
                post.published = True
            post.save()
    # else, no new posts! oh well!

    source.settings = json.dumps(settings_data)
    source.last_checked = now()
    source.save()

    return 'Done!'


@app.route('/external_data_sources/', methods=['POST'])
def external_data_sources_update_all():
    ''' update all external data sources. '''
    sources = [x[0] for x in ExternalSource.select(ExternalSource.id).tuples()]
    return json.dumps([(external_source_run(s), s) for s in sources])

