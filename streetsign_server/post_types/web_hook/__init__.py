'''
    Test module.  This post type, when shown, doesn't display any data, but
    instead sends an ajax POST request to a specified URL, thus allowing the
    presentation to actually control other machines or processes.
'''

__NAME__ = 'Web hook'
__DESC__ = 'Rather than display data, call an external HTTP hook. (Advanced) '''

from flask import render_template_string

from streetsign_server.post_types import my

def form(data):
    ''' the form for editing this type of post '''
    return render_template_string(my('form.html'), **data) #pylint: disable=star-args

def receive(data):
    ''' When the data comes in from the form, what parts do we actually want
        to save? '''

    return {'type':'ajax_hit',
            'render_url': data.get('render_url', ''),
            'display_url': data.get('display_url', ''),
            'hide_url': data.get('hide_url', ''),
            'content':'none'
            }

def display(data): #pylint: disable=unused-argument
    ''' don't actually display anything. '''
    return 'none'

def screen_js():
    ''' return the javascript for doing the dirty work. '''
    return my('screen.js')
