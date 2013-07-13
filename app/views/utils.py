'''
    No actual views in here, only bits and pieces to make views more
    fun.
'''

class PleaseRedirect(Exception):
    ''' so redirects can be passed back to views from logic functions.
        >>> def view_blah(...):
                try:
                    do_stuff()
                except app.PleaseRedirect as e:
                    flash(e.msg)
                    redirect(e.url)
    '''
    def __init__(self, url='index', msg='Something went wrong'):
        self.msg = msg
        self.url = url
