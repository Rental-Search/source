from __future__ import unicode_literals

from os.path import dirname

from eloue.compat.pipeline.conf import settings
from pipeline.compilers.sass import SASSCompiler

class AutoprefixerMixin(object):
    def compile_file(self, infile, outfile, **kwargs):
        super(AutoprefixerMixin, self).compile_file(infile, outfile, **kwargs)
        command = "%s %s %s" % (
            settings.PIPELINE_AUTOPREFIXER_BINARY,
            settings.PIPELINE_AUTOPREFIXER_ARGUMENTS,
            outfile,
        )
        return self.execute_command(command, cwd=dirname(infile))

class AutoprefixerSASSCompiler(AutoprefixerMixin, SASSCompiler):
    pass
