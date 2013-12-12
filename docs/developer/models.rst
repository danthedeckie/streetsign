streetsign_server.models
========================

Where all the Peewee ORM models live.

Useful functions
----------------

.. autofunction:: streetsign_server.models.safe_json_load
.. autofunction:: streetsign_server.models.eval_datetime_formula
.. autofunction:: streetsign_server.models.create_all
.. autofunction:: streetsign_server.models.by_id


Users and Groups
----------------

.. autoclass:: streetsign_server.models.User
   :members:

.. autoclass:: streetsign_server.models.Group
   :members:

.. autoclass:: streetsign_server.models.UserGroup
   :members:


Login Stuff
-----------
Most of the time, these shouldn't be used directly, but instead
use the functions from :doc:`user_session`

.. autoclass:: streetsign_server.models.UserSession
   :members:

.. autofunction:: streetsign_server.models.user_login
.. autofunction:: streetsign_server.models.get_logged_in_user
.. autofunction:: streetsign_server.models.user_logout

And the Invalid Password Exception:

.. autoclass:: streetsign_server.models.InvalidPassword
   :members:


Posts and Feeds
---------------

.. autoclass:: streetsign_server.models.Feed
   :members:

.. autoclass:: streetsign_server.models.FeedPermission
   :members:

.. autoclass:: streetsign_server.models.Post
   :members:

.. autoclass:: streetsign_server.models.ExternalSource
   :members:

Screens and Output
------------------

.. autoclass:: streetsign_server.models.Screen
   :members:

Misc
----

.. autoclass:: streetsign_server.models.ConfigVar
   :members:
