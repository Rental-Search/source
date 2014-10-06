
from itertools import chain

from django.contrib.staticfiles.finders import FileSystemFinder, AppDirectoriesFinder
from django.core.files.storage import FileSystemStorage
from django.template.loaders import filesystem
from django.utils.functional import cached_property

from eloue.compat.pipeline.conf import settings


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
        if path in self.sources:
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
        res = set()
        for elem in chain(settings.PIPELINE_CSS.values(), settings.PIPELINE_JS.values()):
            # TODO: add support for glob
            res.update(elem.get('source_filenames', []))
        return tuple(res)

    @cached_property
    def loader(self):
        """
        Instantiates Loader instance using 'loader_class' attribute
        """
        return self.loader_class()

class PatternFilterMixin(object):
    ignore_patterns = [
        '*.less',
        '*.scss',
        '*.sass',
        '*.coffee',
    ]

    def get_ignored_patterns(self, ignore_patterns):
        return list(set(self.ignore_patterns + ignore_patterns or []))

    def list(self, ignore_patterns):
        ignore_patterns = self.get_ignored_patterns(ignore_patterns)
        return super(PatternFilterMixin, self).list(ignore_patterns)

class AppDirectoriesFinder(PatternFilterMixin, AppDirectoriesFinder):
    """
    Like AppDirectoriesFinder, but doesn't return any additional ignored
    patterns.

    This allows us to concentrate/compress our components without dragging
    the raw versions in via collectstatic.
    """
    pass

class FileSystemFinder(PatternFilterMixin, FileSystemFinder):
    """
    Like FileSystemFinder, but doesn't return any additional ignored patterns

    This allows us to concentrate/compress our components without dragging
    the raw versions in via collectstatic.
    """
    pass
