# -*- coding: utf-8 -*-
#    StreetSign Digital Signage Project
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
#    ---------------------------------

"""
    streetsign_server.views.screens
    -------------------------------

    Views for screen output, and editing the screens.

"""



from flask import render_template, url_for, request, redirect, \
                  flash, json, jsonify
from werkzeug import ImmutableDict

import sqlite3
from glob import glob
from os.path import basename
import urllib
import streetsign_server.post_types as post_types
from streetsign_server import app
from streetsign_server.models import Feed, Post, Screen, ConfigVar, \
                                     config_var, now
from streetsign_server.post_types.image import allow_filetype
from streetsign_server.views.utils import admin_only, registered_users_only
from streetsign_server.views.user_files import user_fonts


def form_json(name, default):
    ''' make sure form input is valid JSON '''
    try:
        return json.dumps(json.loads(request.form.get(name,
                                                      json.dumps(default))))
    except: # pylint: disable=bare-except
        return json.dumps(default)


###########################################
#
# Simple Screen Pages.
#


@app.route('/screens/')
@admin_only('POST')
@registered_users_only('GET')
def screens():
    ''' HTML listing of all screens  '''
    return render_template('screens.html',
                           aliases=config_var('screens.aliases', []),
                           screens=Screen.select())


@app.route('/screens-edit/<screenid>', methods=['GET', 'POST'])
@app.route('/screens-edit/<int:screenid>', methods=['GET', 'POST'])
@admin_only('POST')
@registered_users_only('GET')
def screenedit(screenid):
    ''' edit one screen '''

    try:
        if int(screenid) == -1:
            flash('New Screen')
            screen = Screen() # pylint: disable=no-value-for-parameter
        else:
            screen = Screen().get(Screen.id == int(screenid)) # pylint: disable=no-value-for-parameter

        backgrounds = [basename(x) for x in \
                       glob(app.config['SITE_VARS']['user_dir']  + '*')
                       if allow_filetype(x)]

    except Screen.DoesNotExist:
        flash('Invalid Screen ID! Screen does NOT exist!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form.get('action', 'update') == 'delete':
            screen.delete_instance()
            flash('deleted')
            return redirect(request.referrer)

        # first check that name is OK:
        try:
            oldname = screen.urlname
            screen.urlname = urllib.quote(request.form.get('urlname'), '')
            screen.save()
        except sqlite3.IntegrityError:
            screen.urlname = oldname
            flash("Sorry! That name is already being used!")

        screen.background = request.form.get('background')
        screen.settings = request.form.get('settings', '')
        screen.css = request.form.get('css', '').replace('"', "'")
        screen.zones = form_json('zones', {})
        screen.save()
        flash('saved.')

        if int(screenid) == -1:
            return redirect(url_for('screenedit', screenid=screen.id))

    fonts = ['', 'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy']
    fonts += [name for name, _ in user_fonts()]

    return render_template('screen_editor.html',
                           feeds=Feed.select(),
                           backgrounds=backgrounds,
                           fonts=fonts,
                           screen=screen)


@app.route('/screens/<template>/<screenname>')
def screendisplay(template, screenname):
    '''
        The actual output screen view.
    '''
    try:
        screen = Screen.get(urlname=screenname)
    except Screen.DoesNotExist:
        # return first screen, if you can't find the one we really want.
        # this stops us from ending up with screens which 'die' due to misnaming.
        # They may show the wrong screen - but it's better than not showing
        # a screen at all.
        # TODO: add an config_var to decide what to do in this circumstance.
        screen = Screen.get()

    return render_template('screens/' + template + '.html',
                           screen=screen,
                           site_mode=app.config['MODE'])


@app.route('/screens/posts_from_feeds/<json_feeds_list>')
def screens_posts_from_feeds(json_feeds_list):
    '''
        send JSON list of the posts in whichever feeds you request
        (as a JS array [id,id,id] type list)
    '''
    feeds_list = json.loads(json_feeds_list)

    time_now = now()

    posts = [{"id": p.id,
              "changed": p.write_date,
              "uri": url_for('json_post', postid=p.id)} for p in \
             Post.select().join(Feed)
             .where((Feed.id << feeds_list)
                    &(Post.status == 0)
                    &(Post.active_start < time_now)
                    &(Post.active_end > time_now)
                    &(Post.published)
                   )]
    return jsonify(posts=posts)

@app.route('/screens/json/<int:screenid>', defaults={'old_md5': None})
@app.route('/screens/json/<int:screenid>/<old_md5>')
def screen_json(screenid, old_md5):
    '''
        When you edit a screen, it saves most of the data as JSON.  This
        requests the MD5sum of that data, (and that data).  You can then
        compare against what you're already displaying, and only update
        if it's changed.
    '''

    try:
        screen = Screen.get(id=int(screenid))
    except:
        screen = Screen() # pylint: disable=no-value-for-parameter

    screen_md5 = screen.md5()

    if screen_md5 == old_md5:
        return jsonify(screenid=screenid,
                       md5=screen_md5)
    else:
        return jsonify(screenid=screenid,
                       md5=screen_md5,
                       screen=screen.to_dict())


@app.route('/screens/post_types.js')
def post_types_js():
    '''
        Send the javascript of how to render all the post types. (This is
        stored/generated by the post type modules themselves.)
    '''

    return (render_template('post_types.js', types=post_types.renderers()),
            200, {'Content-Type': 'application/javascript'})

@app.route('/aliases', methods=['GET', 'POST'])
@admin_only('POST')
@registered_users_only('GET')
def save_aliases():
    ''' save the current aliases. '''

    if request.method == 'POST':
        aliases = form_json('aliases', [])

        try:
            alias_configvar = ConfigVar.get(ConfigVar.id == 'screens.aliases')
        except ConfigVar.DoesNotExist:
            alias_configvar = ConfigVar() # pylint: disable=no-value-for-parameter
            alias_configvar.id = 'screens.aliases'
            alias_configvar.save(force_insert=True)

        alias_configvar.value = aliases
        alias_configvar.save()
        return jsonify(aliases=json.loads(alias_configvar.value))

    return jsonify(aliases=config_var('screens.aliases', []))

@app.route('/client/<alias_name>')
def client_alias(alias_name):
    ''' client alias repointing address '''

    raw_aliases = config_var('screens.aliases', [])

    aliases = {}
    for alias in raw_aliases:
        aliases[alias['name']] = alias

    if alias_name in aliases:
        alias = aliases[alias_name]

        # This is very ugly, and could certainly be improved,
        # but it works for now:

        details = []
        if alias.get('forceaspect', None):
            details.append(('forceaspect', alias['forceaspect']))
        if alias.get('forcetop', None) != None:
            details.append(('forcetop', alias['forcetop']))
        if alias.get('fadetime', None) != None:
            details.append(('fadetime', alias['fadetime']))
        if alias.get('scrollspeed', None):
            details.append(('scrollspeed', alias['scrollspeed']))

        request.args = ImmutableDict(**dict(details + request.args.items()))

        return screendisplay(alias['screen_type'], alias['screen_name'])

    else:
        return ('<!doctype html><html><body><h1>Screen Alias not found.</h1>'
                '<p>Sorry...</p><script>'
                'setTimeout(function(){'
                '    document.location.reload(true);}, 10000);'
                '</script></body></html>')
