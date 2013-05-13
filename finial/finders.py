# (c) 2013 Urban Airship and Contributors

from django.contrib.staticfiles.finders import FileSystemFinder

class FinialFileSystemFinder(FileSystemFinder):
    def find(self, path, all=False):
        """We override this to make URL path line up with directory URL."""
        path = '/'.join(path.split('/')[1:])

        return super(FinialFileSystemFinder, self).find(path, all)
