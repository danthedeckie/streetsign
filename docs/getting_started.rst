Getting Started
===============

Hi! Welcome to StreetSign!  I hope you enjoy working with this system as much
as I've enjoyed developing it so far.

Installation instructions are in the Project README file.  It should be very
easy on any linux/OSX or other unixy type computer.

System Requirements
-------------------

- Python 2.7 is recommended, but 2.6 should work too.
- Python development headerfiles & capable compiler:
  `yum install python-devel` on CentOS/RPM based distros,
  `apt-get install python-dev` on Debian/Ubuntu

It's also recommended to install ImageMagick for creating image thumbnails:

- `yum install ImageMagick` (on CentOS/RPM)
  `apt-get install imagemagick` (on Debian/Ubuntu)

Installing
----------

Essentially, once you've downloaded or cloned the project::

    ./setup.sh

Should download and install a virtualenv, and set up all the dependencies and
the initial database (a local sqlite file).  Then ::

    ./run.py

To actually run a local test server.

To deploy streetsign for production use, check out the :doc:`deployment` guide.

The initial administration user 'admin' is created, with a password of 'password'.

If you need to start again with a fresh database, then delete the `database.db` file,
and re-run `./setup.sh`.

This rest of this document hopes to make the different concepts and terminology clear, so
that you can be up to speed as quickly as possible.

Basic Overview
--------------

StreetSign is a Digital Signage system, that makes it easy to display content
on screens & computers around a campus.

It works by having a single 'server', which runs a intranet/web interface
which you can connect to with any web browser, which lets content authors
create items of news which can then be displayed on any screen.

Each physical screen needs a computer (a cheap Raspberry Pi or similar works
fine) connected to it, and to the network, which then connects to the server,
and displays the content in organized layouts, which are specified by the
designer.  These are simple HTML webpages, and simply displayed with a full-
screen web browser. (They can also be connected to by smartphones, tablets,
or other desktop machines if you so desire.)

.. _content_intro:

Content
~~~~~~~

These are the basic pieces of content that you work with:

Posts
`````

Individual items of content, be these news items, photos, clocks, whatever,
are known as 'posts'.  Kind of like on a blog or other news system.  There
are different types of posts: Pure text posts, Picture posts, and 'Rich'
content HTML posts, which can have formatted text, mixing in pictures and
so on as well.

Feeds
`````

Posts are grouped into 'Feeds'.  A specific post can only be in one feed.
This might sound limiting, but don't worry.  You can create as many feeds
as you want, and assign them specific permissions if you need to.

You can have a "latest photos from the campus" feed, a "URGENT" feed, a
"today's joke" feed, a 'urgent things to do' feed, a 'world news from BBC'
feed, or whatever.

A feed can have many different types of posts in it, if you want, and you can
have multiple feeds display in the same places, or have the same feeds display
in different ways on different screens.

External Data Sources
`````````````````````

There are also external data sources, which can open RSS feeds (say the news
from the BBC, or the latest pictures you put on tumblr ...) and import those
as posts into whichever feed you desire.

Posts, when they come in from an external source, can be set to be published
automatically, or not.  You can also edit the posts once they've come in, or
unpublish or delete them.  This is really useful when pulling data from sources
that you're not in complete control of, such as a news feed, or twitter, when
you want editorial control before they go live on screens.

Displaying it all
~~~~~~~~~~~~~~~~~

It's all well and good to have everything organised nicely, but it's only
useful if you can put your content where people can see it...

Publish the posts!
``````````````````

Before the posts will show up anywhere, you will need to set them to be
*published*, which is done on the Feed page.  You can have different users
with permission to do different things - so you can have users who can create
posts, but not publish them, and then a manager's user who can publish them
after approval.

Screens
```````

Full Reference: :doc:`screen_options`

You can design screens, that is, specially taylored output formats for each
display, on the 'screens' area of the web interface.  Each screen will
resize and stretch to try and fit whichever size physical screen you open it
on, but for very different shaped screens (say a tall portrait 9:16 display,
and a 4:3 point of sales screen) you will want to design different layouts.

You can set up specific screens for certain areas, say a dining room screen,
a lounge area screen, a welcome desk one, and so on.


Screen Zones
````````````

Each Screen layout has multiple 'zones' on it.  A zone has it's own position
on the screen, as well as formatting, fonts, etc.  You then tell that zone
to display the posts from as many different feeds as you wish.

If you want, you could have a screen with a left zone which had photos from
two or three different photo feeds, a right zone which showed mainly textual
content about the day's events, and occasional safety notices, and a bottom
scrolling 'ticker' type zone which has world news, and a top 'Clock' zone,
which mainly shows the clock, except when there are urgent announcements, when
it displays those as well.

Dividing content
````````````````

Because you can select multiple feeds to appear in the same zone, and the same
feed can appear on as many screens and zones as you like, you can
easily have announcements specific to certain areas, and general ones.  So you
can have a 'site-announcents' feed, a 'bookstore offers' feed and a 'how much
do drinks cost' feed, say, which are all displayed in the foyer, but the book
store screen only shows the books and site-wide ones, and the coffee bar only
shows the drinks ones, say.

Timing things
~~~~~~~~~~~~~

It's often convinent, especially at conferences, to have announcments which
appear only at certain times of day, such as "what's on next", or "which band
is playing in which venue this evening".

Post Lifetime
`````````````

Each post has a lifetime, which defines when you want it to start appearing on
screens.  So before a conference, you can set up Post items which give the day's
schedule or theme for each day, and set the lifetime on each one to only the day
that it is relevant for.

Time Limits
```````````

As well as the total lifetime of a post, you can also set limitations on what
time of day you want it to be shown.  So you might have a "It's lunchtime,
kids!" message, which lasts the whole length of the conference, but is only
displayed between 12:30 and 1:30.

You can set the time limits for each post to be either "only show this post
during certain times" (useful for dinner time annoucements, say) or to "Don't
show during these specific times" (useful for frivolous/jokey slides which you
don't want up during reflection or meditation times, say.

Permissions
~~~~~~~~~~~

Posts can either be 'published' or not.  If they aren't published, then they
can't be seen by the outside world, and the screens won't display them.  You
can give permission to some users to create posts, but not publish them, if
you desire.  This means you can have content authors who make content for
specific feeds, but you can give publish permission on that feed only to
certain line-managers or communication directors, who then publish the posts.

Permission to change the layout and design of the actual screens can only
be done by "administrators", but still using the web interface.  An
administrator in this sense may well be your graphic designer, which is
fine.  You really need to be trusting your graphic designers, as they
care a lot more about making things look perfect than anyone else, especially
when they are given the tools to do so.

That's it!
~~~~~~~~~~

Hopefully that gives you a good overview of the system, it's designed to be
reasonably easy to work with.

Notes when using the system
---------------------------

There are a few things which it's good to know:

Magic Variables
~~~~~~~~~~~~~~~

In HTML and plain text posts, you can put the following "magic variables":

``%%TIME%%`` and ``%%DATE%%`` which will show up on the output screens as
the current date and time, respectively.

*Note: this time is local to that screen's computer!
So if you are using a raspberry pi or similar, and you're
on a closed network without internet access,
then you'll also need to set up some kind of NTP server too.*

You can customize how the DATE or TIME is formatted using standard
strftime `style formatting tags <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_ after the word DATE or TIME Eg:

``The month is: %%DATE%B%%`` (will show "July" only)

``<h1>%%DATE%B</br>%Y%%</h1>`` (will show "July" and then "2015" on the next line)

It's not recommended to put the current second, as due to the current
design, that will only get updated infreqently, and has no way of guarenteing being right.

Post Sizing/Scaling
~~~~~~~~~~~~~~~~~~~

When posts are displayed on the output screens, they will automatically be
scaled to fit in the zone that they're displayed in.  If you're really
struggling to get text big enough, there's a good chance that you simply have
too much text to fit it all into that zone.

Also, if you have text which is "Title 1" (``<h1>...</h1>`` for the HTML
junkies) it can display as different sizes in different posts, as each post is
scaled independently.

The HTML "rich text" posts are intentionally somewhat limited.  If you want to
have a post where the *design* is important, not just the textual content of
the post, they you should use an external graphic design package, such as
`Inkscape <http://www.inkscape.org>`_ (free), 
`Adobe Illustrator <http://www.adobe.com/uk/products/illustrator.html>`_
(expensive), 
`PixelMator <http://www.pixelmator.com/>`_ (good, not too expensive, mac only`),
and then post as an Image type.
