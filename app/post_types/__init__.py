from os.path import dirname, basename, splitext, isfile
from importlib import import_module
from glob import glob

PATH = dirname(__file__)

_editors = {}

def path_to_module(path):
    return splitext(basename(path))[0]

def modules():
    all_list = [ path_to_module(p) for p in glob(PATH + '/*.py') ]
    all_list.remove('__init__')
    return all_list

def module_dict(name):
    return {'id':name,'name':name}

def types():
    ''' return a list of dicts of all post types.
        TODO: find a way to cache this. '''
    return [ module_dict(m) for m in modules() ]

def load(type_name):
    if type_name in _editors:
        return _editors[type_name]

    #if isfile(PATH + '/' + type_name):
    e = import_module( 'app.post_types.' +  type_name )
    _editors[type_name] = e
    return(e)

def receive(posttype, form):
    editor = load(posttype)
    return(editor.receive(form))

def renderer_js(posttype):
    editor = load(posttype)
    return(editor.renderer_js())

def renderers():
    return [(e, load(e).screen_js()) for e in modules()]
