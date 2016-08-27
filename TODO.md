# In progress

- External Data Sources
- API and other 'public' documentation.
- Unit tests
- RSS "output" of feeds, so mobiles(etc) can subscribe.
- a mobile friendly 'web app' display engine for screen(s).
- a basic 'temporary' auto-screen router which sends different mac addressed or ip addressed
  clients to different actual screens.  This uses a JSON list in a ConfigVar for now.  If this
  system seems to make sense to people, and seems relatively sane, then it can be refactored
  into a new SQL table later (which will be slightly faster...).

## After TS this year:

- rename 'Screen' to 'ScreenLayout'.
- change client aliases to Table based, rather than dumping it all in a single configvar
- 'injest' method on all models, to simplify the form views.  Should then allow validation to
  become a lot more declarative.
- renaming feed(s)

## Urgent:

- config.py way to 'lock' certain users so they can't be deleted...
- make sure user uploaded files have the right place to go etc for new projects,
- should uploaded post images still have their old names?? better that they get given
  `postid-imagename` isn't it?  then there's less chance of confict and over-writing.
- screen restarting every 6 hours or so
- a configvar editor for admins.
- float left/right for images in rich text posts??

## Needed, but copeable for alpha version.

- Better 'CSS' editing for zones and whole-screen.
- Post deactivation -> archive, and archive, future posts, etc view.
- Group Editor, etc.
- Better uploaded files editor.
- Direction for scroller
- abilty to have full-screen URGENT messages.
- RSS post count limiter
- HTML page importer (maybe uses md5? or last-changed? or something to know if it sould make a new post)
- Export Screen Data (JSON) and import.
- Better Post types API (better error messages, etc.)
- way to move posts between feeds
- Templating & defaults for posts?
- 'unarchive' posts.

# Good things for the future:

- Smarter 'live' Screen info updating, w/o reloading the whole page.
- non-session auth as well for API, makes scripting easier.
- Local machine mini-proxy which gets the latest info from the master server,
  but otherwise caches everything and keeps it running locally happily until
  it can connect again.
- favicon & other 'sundries' (404, 301 etc pages)
- replace db.py & run.py with a single manage.py type script
- basic password strength checking
- login attempts counting/stopping
- disallow until attempts \*\* attempts seconds since last attempt?  Then UI does auto-wait after fail (so it doesn't appear to fail, but simply take a long time).
- Better client & serverside validation.
- try/catch enable-able blocks for screens, so that no matter what goes wrong
  with javascript, it somehow notices and reloads the screen, or tells the
  admin, or something.
- better image thumbnails for 'uploaded files' & posts.
  (possibly an auto-cache api, as part of the uploaded files section, which
  then the images `post_type` (plugin) & the display reference?)
  `{{ url_for('thumbnail', filename=...) }}` or something...
- we need some nice default themes
- default screen when the database is first initiated
- default posts when the database is first initiated
- remove old new-post view complexity with choosing types, etc.  It should be done as a single
  view, like the external data importer does.
- urgent alert post type, takes over whole display
- draggable borders of selected zone in the zones editor
- better docs for post types js callbacks
- html5 video post type
- youtube video post type
- clicking on the text box should open up the time select for post lifetime
- by default, don't show old posts
- font select on zones.
- CSS better on zones.
- sub-zones post type, either horizontal or vertical mode, which adds two more zones to the fray, which are faded in and out due to this zone's timing.
- post types add a repr field, also a UUID field, which can be used or set by the external data importers.
- all feeds available as RSS feeds themselves, so streetsign can be a whole news management system.

# Random ideas:

- Extra flag to send to a screen url which would disable setting a background
  (even black) so that it can be embedded easier inside another post?  This would
  allow the "sublayouts" concept (although I imagine performance being an issue).
  Better for sublayouts would be a post type which added new zones to the regular zones list, but had that post div as the parent...


# Things for streetsign 2.0:

- translation & internationalisation/gettext of everything.
- Better "output" / "client" management:
  - Output screens status, tracking which addresses are requesting info,
    alert when one goes down, etc.
- Separate out admin & theme designer roles? or is
  this pointless?
