API/Urls
========

This is a list of the basic API/URLs that streetsign uses, and can be used to
generate other applications (such as a native hardware accelerated client,
for instance.)

All URLs are given in Flask style, so ``<stuff>`` denotes a variable, part
of the URL that changes depending on what you're requesting. ``<int:blah>``
means only accept integer values for ``blah``, etc.

``/screens/<template>/<screenname>``
------------------------------------

Returns the data about this screen, including which zones are defined in it,
which feeds are attached to those zones, etc.  Usually this is called with
the ``basic`` template, which renders the post in place, using their
post type javascript renderers.  This is the main view that normal screen
outputs will use.

``/screens/json/<int:screen_id>``
---------------------------------

Returns the JSON details about a screen.  Which zones it has, CSS, which
zones have what feeds attached, etc.

To save bandwidth, you can call:

``/screens/json/<int:screen_id>/<md5sum>``

with the md5 that was previously given in the screen JSON data, and the 
server will respond with either ONLY the same MD5sum and screen id, or
else with a new MD5sum, and complete new screen JSON data (and id).


``/screens/posts_from_feeds/<[list,of,feed,ids]>``
--------------------------------------------------

Given a json type list of feed ids (``[1,3,2,9,21]``, say), return the JSON
of all posts which are currently active.

Note that for some web servers/requests/proxy systems, you will have to URL
encode the list.  For example: ``/screens/posts_from_feeds/%5B1%2C2%2C%5D``
rather than ``/screens/posts_from_feeds/[1,2]``.  Most web browsers, and
most good HTTP request libraries should do this automatically for you, however.


``/screens/post_types.js``
--------------------------

Returns all the various JSON rendereres that are needed for drawing posts
to a screen zone.

