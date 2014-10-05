from __future__ import unicode_literals

import os
from os.path import dirname, commonprefix, relpath, join, exists

from eloue.compat.pipeline.conf import settings
from pipeline.compilers import sass


class OutputPathMixin(object):
    static_dir = settings.STATICFILES_DIRS[0]

    def output_path(self, path):
        for d in settings.TEMPLATE_DIRS:
            prefix = commonprefix((path, d))
            if prefix:
                output = join(self.static_dir, relpath(path, prefix))
                output_path = dirname(output)
                if not exists(output_path):
                    os.makedirs(output_path)
                return output
        return output

    def compile_file(self, infile, outfile, **kwargs):
        outfile = self.output_path(outfile)
        return super(OutputPathMixin, self).compile_file(infile, outfile, **kwargs)

class AutoprefixerMixin(object):
    def compile_file(self, infile, outfile, **kwargs):
        super(AutoprefixerMixin, self).compile_file(infile, outfile, **kwargs)
        command = "%s %s %s" % (
            settings.PIPELINE_AUTOPREFIXER_BINARY,
            settings.PIPELINE_AUTOPREFIXER_ARGUMENTS,
            outfile,
        )
        return self.execute_command(command, cwd=dirname(outfile))

class AutoprefixerSASSCompiler(OutputPathMixin, AutoprefixerMixin, sass.SASSCompiler):
    pass
