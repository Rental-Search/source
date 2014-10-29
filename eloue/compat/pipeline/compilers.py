from __future__ import unicode_literals

import os
from os.path import dirname, commonprefix, relpath, join, exists

from django.dispatch.dispatcher import receiver
from django.contrib.staticfiles import finders

from eloue.compat.pipeline.conf import settings
from pipeline.compilers import sass, SubProcessCompiler
from pipeline.signals import js_compressed


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
        print infile, outfile
        command = "%s %s %s" % (
            settings.PIPELINE_AUTOPREFIXER_BINARY,
            settings.PIPELINE_AUTOPREFIXER_ARGUMENTS,
            outfile,
        )
        return self.execute_command(command, cwd=dirname(outfile))

class AutoprefixerSASSCompiler(OutputPathMixin, AutoprefixerMixin, sass.SASSCompiler):
    pass

class RequireJsCompiler(SubProcessCompiler):
    output_extension = 'js'

    def match_file(self, filename):
        return filename.endswith('.js')

    def compile_file(self, infile, outfile, **kwargs):
        command = "%s %s -o %s out=%s" % (
            settings.PIPELINE_RJS_BINARY,
            settings.PIPELINE_RJS_ARGUMENTS,
            infile,
            outfile,
        )
        return self.execute_command(command, cwd=dirname(outfile))

@receiver(js_compressed, dispatch_uid='pipeline_requirejs_build')
def requirejs_build(sender, package, **kwargs):
    if 'requirejs' in package.extra_context:
        # get full path to the build.js file on local FS
        input_path = package.extra_context['build']
        infile = finders.find(input_path)

        # calculate full path to destination file
        path = input_path
        output_path = infile
        while path != '':
            path = dirname(path)
            output_path = dirname(output_path)
        outfile = join(output_path, package.output_filename)

        # run r.js compiler
        RequireJsCompiler(sender.verbose, sender.storage).compile_file(infile, outfile)

        # compress and save to the storage
        content = sender.compressor.compress_js([package.output_filename], **kwargs)
        sender.save_file(package.output_filename, content)
