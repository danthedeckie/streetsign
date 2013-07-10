from flask import render_template, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
from glob import glob
from os.path import basename, dirname, join as pathjoin, splitext, isdir, isfile
from werkzeug import secure_filename
from os import makedirs, remove, stat
from app import app


##################################################################
# user uploaded files:

# TODO: move to file upload lib.
def allow_filetype(filename):
    return splitext(filename)[-1].lower() in \
        ['.png','.jpg','.jpeg','.gif','.bmp','.svg']

def make_dirlist(path):
    return_list = []
    things = glob(pathjoin(g.site_vars['user_dir'],path,'*'))
    for f in things:
        name = basename(f)
        if isdir(f):
            return_list.append(
                { 'name': name + '/',
                   'url': name + '/',
                  'size': "{0} items".format(len(glob(pathjoin(f,'*')))) })
        else:
            return_list.append(
                { 'name': name,
                   'url': pathjoin(g.site_vars['user_url'],path,name),
                  'size': stat(f).st_size })
    return return_list

@app.route('/user_files/', methods=['GET','POST'])
@app.route('/user_files/<path:dirname>', methods=['GET','POST'])
def user_files_list(dirname=""):
    user = user_session.get_user()

    full_path = pathjoin(g.site_vars['user_dir'],dirname)

    if not isdir(full_path):
        makedirs(full_path)

    if request.method == 'POST' and user.is_admin:
        if request.form.get('action') == 'upload':
            f = request.files['image_file']
            if f and allow_filetype(f.filename):
                filename = secure_filename(f.filename)
                f.save(pathjoin(full_path, filename))
                flash('Uploaded file:'+filename)
            else:
                flash('Sorry. Invalid Filetype')
        elif request.form.get('action') == 'delete':
            filename = secure_filename(request.form.get('filename'))
            full_filename = pathjoin(full_path, filename)
            remove(full_filename)
            flash('Deleted '+ filename)


    files = make_dirlist(dirname)

    return render_template('user_files.html',
                           full_path = full_path,
                           file_list = files,
                           dirname=dirname)

