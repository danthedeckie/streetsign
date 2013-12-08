# In progress

- Bootstrapification
  - why are chosen/select boxes funny sizes?

# Sort of next

- WYSIWYG editor for HTML posts. (bootstrap-wysihtml5) (with note that for more complex things, really it should be done as a designed image...)
- Data puller
- API and other 'public' documentation.

# Bugs:

- Single message on side-scrolling zone displays only once.

## Urgent:

- make sure user uploaded files have the right place to go etc for new projects,
- make lack of thumbnail generator not an exception, but fall back happily.

## Needed, but copable for alpha version.

- Dropdown select box for font for screen zones (easy)
- Better 'CSS' editing for zones and whole-screen.
- Smarter 'live' Screen info updating, w/o reloading the whole page.
- Post deactivation -> archive, and archive, future posts, etc view.
- Group Editor, etc.
- Better uploaded files editor.
- Direction for scroller
- Add waitress or cherrypy scripts for basic stand-alone server.

# Good things for the future:

- non-session auth as well for API, makes scripting easier.
- 'create feeds from twitter/RSS/etc' importers? scripts, with cron???
- Full Documentation
- Output screens status, tracking which addresses are requesting info, alert when one goes down, etc.
- Local machine mini-proxy which gets the latest info from the master server, but otherwise caches everything
  and keeps it running locally happily until it can connect again.
- Icons
- favicon & other 'sundries' (404, 301 etc pages)
- Unit tests
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
  then the images post_type (plugin) & the display reference?)
  {{ url_for('thumbnail', filename=...) }} or something...

# Random ideas:

- Feed type options:
  - Locally fed (as normal)
  - From RSS feed
  - From twitter?
  etc
  (rather than weird 'RSS' _post_ type a la concerto)
- or would 'feed' level things be better? where you could have the feed 'controlled' by either rss/json/html, or whatever??
