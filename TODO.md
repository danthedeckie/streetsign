# In progress

# Missing basic Features

## Urgent:

- More polished GUI.

## Needed, but copable for alpha version.

- Dropdown select box for font for screen zones (easy)
- Better 'CSS' editing for zones and whole-screen.
- Smarter 'live' Screen info updating, w/o reloading the whole page.
- Post deactivation -> archive, and archive, future posts, etc view.
- WYSIWYG editor for HTML posts.
- Group Editor, etc.
- Better uploaded files editor.

# Good things for the future:

- New name
- Full Documentation
- Output screens status, tracking which addresses are requesting info, alert when one goes down, etc.
- Local machine mini-proxy which gets the latest info from the master server, but otherwise caches everything
  and keeps it running locally happily until it can connect again.
- Icons
- clean up CSS. possibly with LESS or similar?
- favicon & other 'sundries' (404, 301 etc pages)
- Unit tests
- move app/ dir to whatever the project ends up being called.
- replace db.py & run.py with a single manage.py type script
- Internationalisation / multilingual stuff.
- basic password strength checking
- login attempts counting/stopping
- Better client & serverside validation.
- try/catch enable-able blocks for screens, so that no matter what goes wrong with javascript,
  it somehow notices and reloads the screen, or tells the admin, or something.

# Random ideas:

- Feed type options:
  - Locally fed (as normal)
  - From RSS feed
  - From twitter?
  etc
  (rather than weird 'RSS' _post_ type a la concerto)
