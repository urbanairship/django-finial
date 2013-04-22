django-finial
=============

Hierarchical template overriding on a per request basis.


Definition
----------
fin·i·al  
`/finēəl/`
*Noun*

![Alt text](finial.png "Example of a finial in architecture.")

1. A distinctive ornament at the apex of a roof, pinnacle, canopy, or
similar structure.
2. An ornament at the top, end, or corner of an object such as a post,
piece of furniture, etc.

You might see the relation given that this project's goal is to create a
sparse branch of templates for each override, thus "decorating" the
"top" of your existing templates hierarchy.

What's it for?
--------------

Any circumstance in which you wish to do A/B testing, or do dark-launches, or even
include user-specified theming (although, it's a bit heavy for general purpose use),
you can use django-finial to do that for you. 

It's especially nice when you're not able or not willing to have multiple versions
of your software stack deployed in order to get A/B. This allows you to do all of your
A/B testing on the same branch/checkout.


How it works
------------

Principally, Finial works at the middleware layer of the request/response cycle.
If request.user is logged in and said user has overrides defined, finial will rearrange 
the order of ```STATICFILES_DIRS```, and ```TEMPLATE_DIRS``` such that their resources
will be loaded before the 'default' ones. 

There are other features which enable you to override URL paths to views, template_tags to
specify URLS for certain assets in your templates, and helpers that will build the URLConf
settings necessary to host static assets locally for all of your overrides.

How to install it
-----------------

Installation is easy to get started, but can be quite customized.

For basic use:

* Install the package ```(virtualenv)# pip install django-finial```
* Add ```finial``` to your list of INSTALLED_APPS in ```settings.py```
* Run ```python manage.py migrate``` to pick up migrations and table creations

This allows you to override template loading. But it only gets you so far -- you may need
to have an override-prefix for finial to use to find your tempalte directories.

Put this in your ```settings.py``` to have finial look in ```/path/to/django/overrides/<override_name>_templates/```

```python
FINIAL_LOCAL_DIR_PREFIX = '/overrides' # This is the directory prefix from your PROJECT_PATH
```
See ```example_settings.py``` for other common settings




