# In progress

- Bootstrapification
- External Data Sources
- API and other 'public' documentation.
- Unit tests

# Bugs:

- Single message on side-scrolling zone display doesn't go on for ever (some kind of timeout/race condition?)
- Test Firefox memory usage on screens display.

## Urgent:

- make sure user uploaded files have the right place to go etc for new projects,
- make lack of thumbnail generator not an exception, but fall back happily.
- remove to archive and finally deletion of old posts & related files/content.

## Needed, but copable for alpha version.

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

# Random ideas:

- Would a CSS 'marquee' work better for scrolling, rather than jQuery?  Each
  element inside the marquee could be a span within it....
  I don't know if this would make posts going inactive while 'live' look ugly,
  though...
- Extra flag to send to a screen url which would disable setting a background
  (even black) so that it can be embedded easier inside another post?  This would
  allow the "sublayouts" concept (although I imagine performance being an issue).
