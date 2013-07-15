from flask import render_template_string, url_for, json, request, g
from werkzeug import secure_filename
from os.path import splitext, join as pathjoin, isdir, abspath
from os import makedirs

def my(ending):
    ''' given '.html', returns (if this is the foobar module)
        the contents of: /where/this/file/is/foodbar.html '''

    with open(splitext(abspath(__file__))[0] + ending,'r') as f:
        return f.read()

def allow_filetype(filename):
    return splitext(filename)[-1].lower() in \
        ['.png','.jpg','.jpeg','.gif','.bmp','.svg']

def form(data):
    return render_template_string(my('.form.html'), **data)

def receive(data):
    if 'upload' in data:
        f = request.files['image_file']
        if f and allow_filetype(f.filename):
            filename = secure_filename(f.filename)
            where = pathjoin(g.site_vars['user_dir'],'post_images')
            if not isdir(where):
                makedirs(where)

            f.save(pathjoin(where, filename))
        else:
            raise IOError('Invalid file. Sorry')
    else:
        filename = data.get('filename')
        if filename and allow_filename(filename):
            filename = secure_filename(filename)
        else:
            raise Exception('Tried to change the file, huh? Not happening')
            # TODO

    return {'content': filename,
            'filename': filename,
            'file_url': g.site_vars['user_url']+'/post_images/'+filename}

def display(data):
    return ('<img class="post_image" src="{0}"'
           ' style="width:100%;height:auto" />'.format(data['file_url']))

def screen_js():
    return my('.screen.js')
