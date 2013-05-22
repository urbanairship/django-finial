# (c) 2013 Urban Airship and Contributors

import os
import simplejson as json

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.conf import settings

from finial import util

class Command(BaseCommand):
    help = 'Querys local file system to populate override manifests'

    def handle(self, *args, **kwargs):
        # Assumes that your static media is always in a
        # ``<project_path>/static/`` root. Mileage may vary.
        static_override_root = os.path.join(
            settings.PROJECT_PATH, 'static', settings.FINIAL_URL_PREFIX
        )
        self.stdout.write('Found static override root: {0}'.format(
            static_override_root
        ))

        override_files = util.get_static_override_files(static_override_root)
        for override in override_files:
            self.stdout.write('Caching manifest for override: {0}'.format(override))
            self.stdout.write('\t with these files: {0}\n\n'.join(
                '\n\t'.join(override_files[override])
            ))
            cache.set(
                util.get_override_manifest_cache_key(override),
                json.dumps(override_files[override]),
                0 # We don't want these to ever automaticall expire!
            )
