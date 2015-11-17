from django.core.management.commands import makemessages


from django.utils.translation import trans_real

try:
    from django.utils.encoding import force_text as to_text
except ImportError:
    from django.utils.encoding import force_unicode as to_text

from eloue.compat.pyjade.loader import Loader

from django.conf import settings

def decorate_templatize(func):
    def templatize(src, origin=None):
        src = to_text(src, settings.FILE_CHARSET)

        loader = Loader((
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ))

        if loader.is_jade(origin):
            html = loader.process_jade(src, origin)
        else:
            html = src

        return func(html, origin)

    return templatize

trans_real.templatize = decorate_templatize(trans_real.templatize)



class Command(makemessages.Command):

	def handle_noargs(self, *args, **options):
		options['ignore_patterns'] = ['env/*', 'node_modules/*', 'bower_components']
		options['extensions'] = ['html', 'txt', 'jade']
		super(Command, self).handle_noargs(*args, **options)
	