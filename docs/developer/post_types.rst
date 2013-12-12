streetsign_server.post_types
============================

Post types are the different kinds of posts. So plain text posts, rich html
posts, image posts, etc.  Each type is defined in its own module here, so
it's easy to add your own.

As well as the ``.py`` module, there's also usually a ``.screen.js`` javascript
file which contains the output screen javascript for rendering it again at the
other end, and a ``.form.html`` file, which is the template used by the
individual module to render the form for editing that type of post.

Any other bits and pieces you need for this specific post type should be kept
here with the module.

Post Type Generic Module Overview
---------------------------------

As each type of post is different, and has different data storage requirements
in the database, and doesn't have to be queried against, there is no point in
having some complex database schema to cope with all possibilities.

Instead, there are columns in the database for storing things common to all
posts, and which are queried against, such as lifetime, etc. There is also
a CharField textual field which stores post-type-specific data in it as JSON.

Each post-type module doesn't need to do the json dumping and loading, that's
done further up the chain.  Instead, the module functions are handed standard
python dicts (``{"thing": "value"}``), to work with.  When they return those
dicts, they get bundled back into JSON and stuffed in the database.

So you will need to be careful not to try and store things which aren't
JSONable.


Inside each module,
~~~~~~~~~~~~~~~~~~~

You need the following functions:

.. function:: form(data)

   return the html for the form for editing this kind of post.
   ``data`` is, of course, the data last saved and to be displayed
   in the form.

.. function:: receive(data)

   when the form is submitted, this function will be send the request.form
   data, which you should now extract the relevant info from, sanitize!!,
   and then this function should return the data you want to store in the
   database about this post.

.. function:: display(data)

   if you need to do anything to the data before it gets sent on to the
   screen (as json) to be displayed, this is the place to do it.

.. function:: screen_js()

   return the javascript object used to render this item on the screen
   client side.

Rendering Screen Zones
----------------------

.. automodule:: streetsign_server.post_types
   :members:

.. automodule:: streetsign_server.post_types.html
   :members:

.. automodule:: streetsign_server.post_types.text
   :members:

.. automodule:: streetsign_server.post_types.image
   :members:

And finally
-----------

There is also a 'weird' experimental web-hook post type included.
If you find it confusing for your users, feel free to remove it.

.. automodule:: streetsign_server.post_types.web_hook
   :members:
