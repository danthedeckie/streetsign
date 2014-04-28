# In progress

- External Data Sources
- API and other 'public' documentation.
- Unit tests
- reworking animation in screens display to use CSS3 keyframe animations, and much less 'janky' callbacks, etc. (dev branch)

# Bugs:

- Single message on side-scrolling zone display doesn't go on for ever (some kind of timeout/race condition?)

## Urgent:

- make sure user uploaded files have the right place to go etc for new projects,
- make lack of thumbnail generator not an exception, but fall back happily.
- remove to archive and finally deletion of old posts & related files/content.
- HTML posts color css classes

## Needed, but copeable for alpha version.

- delete posts and publish/unpublish should be faster, using ajax.
- there should be a 'show old posts' toggle (with cookie)
- Dropdown select box for font for screen zones (easy)
- Better 'CSS' editing for zones and whole-screen.
- Smarter 'live' Screen info updating, w/o reloading the whole page.
- Post deactivation -> archive, and archive, future posts, etc view.
- Group Editor, etc.
- Better uploaded files editor.
- Direction for scroller
- abilty to have full-screen URGENT messages.
- A bunch of good default background images.
- RSS post count limiter
- HTML page importer (maybe uses md5? or last-changed? or something to know if it sould make a new post)
- Export Screen Data (JSON) and import.
- Post Types (and External Data Types) should have a 'display name' property.
- Better Post types API (better error messages, etc.)
- move post types into their own folders, like external_post_types.

# Good things for the future:

- non-session auth as well for API, makes scripting easier.
- Output screens status, tracking which addresses are requesting info, alert when one goes down, etc.
- Local machine mini-proxy which gets the latest info from the master server, but otherwise caches everything
  and keeps it running locally happily until it can connect again.
- favicon & other 'sundries' (404, 301 etc pages)
- replace db.py & run.py with a single manage.py type script
- Internationalisation / multilingual stuff.
- basic password strength checking
- login attempts counting/stopping
- disallow until attempts \*\* attempts seconds since last attempt?  Then UI does auto-wait after fail (so it doesn't appear to fail, but simply take a long time).
- Better client & serverside validation.
- try/catch enable-able blocks for screens, so that no matter what goes wrong
  with javascript, it somehow notices and reloads the screen, or tells the
  admin, or something.
- image thumbnails for 'uploaded files' & posts.
  (possibly an auto-cache api, as part of the uploaded files section, which
  then the images `post_type` (plugin) & the display reference?)
  `{{ url_for('thumbnail', filename=...) }}` or something...

- we need some nice default themes
- default screen when the database is first initiated
- default posts when the database is first initiated
- remove old new-post view complexity with choosing types, etc.  It should be done as a single
  view, like the external data importer does.
- post types as their own dir/packages, rather than all being jumbled together.
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
- post types add a repr field, also a UUID field, which can be used or set by the external data importes.

# Random ideas:

- Extra flag to send to a screen url which would disable setting a background
  (even black) so that it can be embedded easier inside another post?  This would
  allow the "sublayouts" concept (although I imagine performance being an issue).
  Better for sublayouts would be a post type which added new zones to the regular zones list, but had that post div as the parent...
