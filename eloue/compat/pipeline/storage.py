from pipeline import storage

class SafeUrlCachedFilesMixin(object):
    def url(self, name, force=False):
        try:
            return super(SafeUrlCachedFilesMixin, self).url(name, force=force)
        except:
            pass
        return name

class PipelineCachedStorage(SafeUrlCachedFilesMixin, storage.PipelineCachedStorage):
    pass
