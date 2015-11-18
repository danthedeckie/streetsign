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
    streetsign_server.views.user_files
    ----------------------------------

    Views for working with user-uploaded files.

"""


from flask import render_template, request, redirect, \
                  flash, g, url_for, Response
import streetsign_server.user_session as user_session
from streetsign_server.views.utils import admin_only, registered_users_only

from glob import glob
from os.path import basename, dirname, join as pathjoin, splitext, isdir, isfile
from werkzeug import secure_filename # pylint: disable=no-name-in-module
from os import makedirs, remove, stat
from streetsign_server import app
from subprocess import check_call # for making thumbnails

##################################################################
# user uploaded files:

def human_size_str(filename):
    ''' returns a human-readable size (string) of a file-name '''
    s = stat(filename).st_size
    if s > 1048576:
        return str(s/1048576) + 'MB'
    if s > 1024:
        return str(s/1024) + 'kB'

# TODO: move to file upload lib.


IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']
ALLOWED_FORMATS = IMAGE_FORMATS + ['.ttf', '.otf']

def allow_filetype(filename):
    ''' is this file-type allowed to be uploaded? '''
    return splitext(filename)[-1].lower() in ALLOWED_FORMATS

def make_dirlist(path):
    ''' returns a list of the files and sub-dirs in a directory, ready to be
        JSON encoded, and sent to a client, or rendererd server-side. '''

    return_list = []
    things = glob(pathjoin(g.site_vars['user_dir'], path, '*'))
    for f in things:
        name = basename(f)
        if isdir(f):
            return_list.append(
                {'name': name + '/',
                 'url':  name + '/',
                 'size': "{0} items".format(len(glob(pathjoin(f, '*'))))})
        else:
            if allow_filetype(name):
                thumb = '<img src="{0}" alt="{1}" />'.format(
                    url_for('thumbnail', filename=path + name),
                    name)
            else:
                thumb = ''

            return_list.append(
                {'name':  name,
                 'thumb': thumb,
                 'url':   pathjoin(g.site_vars['user_url'], path, name),
                 'size':  human_size_str(f)})
    return return_list

@app.route('/user_files/', methods=['GET', 'POST'])
@app.route('/user_files/<path:dir_name>', methods=['GET', 'POST'])
@admin_only('POST')
@registered_users_only('GET')
def user_files_list(dir_name=""):
    ''' HTML list of user-uploaded files. '''

    user = user_session.get_user()

    full_path = pathjoin(g.site_vars['user_dir'], dir_name)

    if not isdir(full_path):
        makedirs(full_path)

    if request.method == 'POST' and user.is_admin:
        if request.form.get('action') == 'upload':
            f = request.files['image_file']
            if f and allow_filetype(f.filename):
                filename = secure_filename(f.filename)
                f.save(pathjoin(full_path, filename))
                flash('Uploaded file:' + filename)
            else:
                flash('Sorry. Invalid Filetype')
        elif request.form.get('action') == 'delete':
            filename = secure_filename(request.form.get('filename'))
            full_filename = pathjoin(full_path, filename)
            remove(full_filename)
            flash('Deleted ' + filename)


    files = make_dirlist(dir_name)

    return render_template('user_files.html',
                           full_path=full_path,
                           file_list=files,
                           dirname=dir_name)

@app.route('/thumbnail/<path:filename>')
def thumbnail(filename):
    ''' return a thumbnail of an (image) file.  if one doesn't exist,
        create one (with imagemagick(convert)) '''

    full_path = pathjoin(g.site_vars['user_dir'], filename)
    thumb_path = pathjoin(g.site_vars['user_dir'], '.thumbnails', filename)

    if splitext(filename)[-1].lower() not in IMAGE_FORMATS:
        return 'not an image I will not make a thumbnail.'

    if isfile(full_path):
        if not isfile(thumb_path):
            # we need to make a thumbnail!
            where = pathjoin(g.site_vars['user_dir'],
                             '.thumbnails',
                             dirname(filename))
            if not isdir(where):
                makedirs(where)

            try:
                check_call([pathjoin(g.site_vars['site_dir'],
                                     'scripts',
                                     'makethumbnail.sh'),
                           full_path, thumb_path])
            except:
                return 'Sorry!'
        # either there is a thumbnail, or we just made one.
        return redirect(g.site_vars['user_url'] + '/.thumbnails/' + filename)
    else:
        return 'Sorry! not a valid original file!'

def user_fonts():
    ''' return a list of (name, url) tuples for all user-available fonts. 
    '''
    fonts = []

    for f in glob(app.config['SITE_VARS']['user_dir']+ 'fonts/*tf'):
        name = splitext(basename(f))[0]
        url = url_for('static', filename='user_files/fonts/' + basename(f))
        fonts.append((name, url))
    return fonts


@app.route('/user_files/fonts.css')
def user_fonts_css():
    ''' return a CSS file with @font-face definitions for each font in the user
        uploaded fonts directory '''
    fonts = user_fonts()
    css_fonts = []
    for name, url in fonts:
        css_fonts.append(
            '@font-face {font-family: %s; src:url(%s)}' % (name, url)
            )

    return Response('\n'.join(css_fonts), status=200, mimetype='text/css')
