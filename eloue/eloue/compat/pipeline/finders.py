
from itertools import chain

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
        # the code below has been taken from TemplateLoader class
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
        for source in self.sources:
            if self.filenames_match(path, source):
                for match in self.loader.get_template_sources(path):
                    if not all:
                        return match
                    matches.append(match)
        return matches

    def list(self, *args):
        """
        Returns empty list in order to hide source files from been automatically collected
        """
        return []

    @cached_property
    def sources(self):
        """
        Collects source file names from PIPELINE_CSS and PIPELINE_JS dictionaries
        """
        res = []
        for elem in chain(pl_settings.PIPELINE_CSS.values(), pl_settings.PIPELINE_JS.values()):
            res.extend(elem.get('source_filenames', []))
        return res

    def filenames_match(self, path, source):
        """
        Checks if two file names match:
            1. file names without extension are equal
            2. requested file's extension is one of known translation targets (e.g. .css)
        """
        if source == path:
            return True

        path_name, path_ext = os.path.splitext(path)
        source_name = os.path.splitext(source)[0]

        # SCSS >= 3.3 compiles into 2 files, .css and .css.map
        if path.endswith('.css.map'):
            path_name, path_ext = os.path.splitext(path_name)

        if path_name == source_name and path_ext in ('.css', '.js'):
            return True

    @cached_property
    def loader(self):
        """
        Instantiates Loader instance using 'loader_class' attribute
        """
        return self.loader_class()
