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
* Add ```finial.middleware.TemplateOverrideMiddleware``` to your project's middleware tuple
(someplace after Session and Authentication)
* Add ```finial.context_processors.asset_url``` to your ```TEMPLATE_CONTEXT_PROCESSORS``` tuple.
* Run ```python manage.py migrate``` to pick up migrations and table creations

This allows you to override template loading. But it only gets you so far -- you may need
to have an override-prefix for finial to use to find your tempalte directories.

Put this in your ```settings.py``` to have finial look in ```/path/to/django/overrides/<override_name>_templates/```

```python
FINIAL_LOCAL_DIR_PREFIX = '/overrides' # This is the directory prefix from your PROJECT_PATH
```
See ```example_settings.py``` for other common settings


Getting Started
---------------

There are three different systems at work in Finial: 

 1. Template Overrides -- short circuit template loader to load your overridden template first.
 2. URLConf Overrides -- create a request.urlconf which puts the override url patterns first.
 3. Staticfiles Overrides -- short circuit staticfiles loaders to load contents from override dirs.

**Template Overrides**

These are the most straight forward of the three mechanisms. Basically, it takes advantage of the fact that django
will return the first template whose name matches the one requested by a view's response constructor. It does this
by shuffling the order of the ```TEMPLATE_DIRS``` in settings on a per request basis in Finial's ``middleware``. Finial will
look for users who have overrides enabled; when it finds them it takes all of the overrides for the given user and 
rearranges the directory structure for ```TEMPLATE_DIRS``` in override priority order.

Priority, in our case, assumes that lower is more important. So an override with a priority of 1 should always win out.

**URLConf Overrides**

These are a little more complex, but you can opt to use these when you need to have fundamental changes to view logic
for a given url endpoint. It allows you to (again on a per request basis) shuffle the ordering of urlpatterns so 
an overridden view can be used in place of the default view for a given url pattern. 

We do this using the django machinery which checks each request object for a ```request.urlconf``` attribute. If it finds
this, then it ignores the root URLConf.

Finial knows to setup this request.urlconf by looking at your override urlconf module (has to be its own module) path in
```settings.py```. We look for a dictionary of override names to urlconf import strings like the following:

```python

FINIAL_URL_OVERRIDES = {
    'my_override': 'my_project.my_override_finial_patterns'
}
```

**Staticfiles Overrides**

Oddly, this is the most complex of the three situations. While traditional HTTP servers were designed only with static
contents in mind -- django's highly dynamic nature puts it at odds with static media.

We have two areas in which we have to do pretty radically different things. In development, we need django so serve
our content. In production we generally have static media hosted by a different domain entirely (S3, CDNs, etc.). To
address these differences we have a couple of helper methods to sort things out:

**Local Development with Staticfiles Overrides**

In this situation people often setup custom django url endpoints to serve the static media from a checkout of their
project locally.

```python
if settings.DEBUG:
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT}),
    )
```

So, to get do the same for all of the overrides we're testing locally, we need a separate url endpoint for each one:

```python

if settings.DEBUG:
    # Remember to do this BEFORE regular staticfiles serving.
    urlpatterns = finial_shortcuts.create_local_override_urls(urlpatterns)
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT}),
    )
```
You'll notice that a lot of whether you're developing locally or working in production is determined by the ```settings.DEBUG``` flag.
If you use some other variable for this, make sure that it mimics DEBUG.

However, there's still one more thing you must do to get your static media to load properly for local development.
Make sure to prepend your ```settings.STATICFILES_FINDERS``` with ```finial.finders.FinialFileSystemFinder```.

Your ```local_settings.py``` should look something like this for staticfiles configurations:

```python

DEBUG=True
PROJECT_PATH = '/path/to/django/root/'
FINIAL_URL_VERSION_PREFIX = 'deploy5-'
FINIAL_STATIC_URL_PREFIX = 'https://s3.amazonaws.com/com.finial.media'
FINIAL_LOCAL_DIR_PREFIX = '/overrides'
STATICFILES_FINDERS = (
    'finial.finders.FinialFileSystemFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
```

_Note_: If we want to not require all of our overrides directories to live in our project root, we need to specify
a ```FINIAL_LOCAL_DIR_PREFIX``` which is applied after the ```PROJECT_PATH``` variable. The 'root' override directory
from the example above would be ```/path/to/django/root/overrides/```.


**Production with Staticfiles Overrides**

Again, we know we're in production based on the ```settings.DEBUG``` value being ```False```. In that case instead of using local paths,
we construct a URL using ```settings.FINIAL_STATIC_URL_PREFIX```, the override name, and optionally a deploy version (
specified with ```settings.FINIAL_URL_VERSION_PREFIX```

The URLs for these assets are determined by the template context processor that we installed in our ```settings.TEMPLATE_CONTEXT_PROCESSORS```
back in the begining.


**Directory Structure**

Since templates and staticfiles are so totally different, we keep them in separate directory structures.

```
~/path/to/django/overrides/$ tree
.
├── test_or_staticfiles
│   └── images
│       ├── configure-image.png
│       └── docs-image.png
└── test_or_template
    ├── apps
    │   └── view.html
    └── base.html

4 directories, 4 files
```
