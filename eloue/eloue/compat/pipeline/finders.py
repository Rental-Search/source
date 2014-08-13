
import os.path

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.template.loaders import filesystem
from django.utils.functional import cached_property

from pipeline.conf import settings as pl_settings

class TemplatesFileSystemFinder(FileSystemFinder):
    loader_class = filesystem.Loader

    def __init__(self, *args, **kwargs):
        super(TemplatesFileSystemFinder, self).__init__(*args, **kwargs)
        for root in settings.TEMPLATE_DIRS:
            prefix = ''
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            root = filesystem_storage.location
            self.locations.append((prefix, root))
            self.storages[root] = filesystem_storage

    def find(self, path, all=False):
        """
        Looks for files in PIPELINE_CSS and PIPELINE_JS
        """
        matches = []
        for elem in pl_settings.PIPELINE_CSS.values():
            for source in elem.get('source_filenames', []):
                if source == path or os.path.splitext(path) == (os.path.splitext(source)[0], '.css'):
                    for match in self.loader.get_template_sources(path):
                        if not all:
                            return match
                        matches.append(match)
        return matches

    def list(self, *args):
        return []

    @cached_property
    def loader(self):
        return self.loader_class()
