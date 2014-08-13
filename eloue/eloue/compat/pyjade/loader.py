
from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader, find_template_loader
from django.utils.functional import cached_property

from pyjade.utils import process

from .compiler import Compiler
from .parser import Parser

class Loader(BaseLoader):
    is_usable = True

    def __init__(self, loaders):
        self._loaders = loaders

    @cached_property
    def loaders(self):
        # Resolve loaders on demand to avoid circular imports
        cached_loaders = [find_template_loader(loader) for loader in self._loaders]
        # Return cached_loaders to be stored atomically. Otherwise, another thread
        # could see an incomplete list. See #17303.
        return cached_loaders

    def is_jade(self, template_name):
        return template_name.endswith('.jade')

    def process_jade(self, source, template_name):
        return process(source, filename=template_name, parser=Parser, compiler=Compiler)

    def load_template_source(self, template_name, template_dirs=None):
        is_jade = self.is_jade(template_name)
        for loader in self.loaders:
            try:
                source, origin = loader.load_template_source(template_name, template_dirs)
                # process Jade
                if is_jade:
                    source = self.process_jade(source, template_name)
                return source, origin
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(template_name)
