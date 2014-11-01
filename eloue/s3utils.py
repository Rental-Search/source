from django.utils.functional import SimpleLazyObject
from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin

from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
from boto.utils import parse_ts


from eloue.compat.pipeline.storage import SafeUrlCachedFilesMixin
from django.core.cache import cache

class S3BotoStorageCached(S3BotoStorage):
	def exists(self, name):
		name = self._normalize_name(self._clean_name(name))
		if self.entries:
			return name in self.entries
		if cache.get(self._encode_name(name)):
			return True
		else:
			k = self.bucket.new_key(self._encode_name(name))
			cache.set(self._encode_name(name), k)
		return k.exists()



class S3PipelineStorage(SafeUrlCachedFilesMixin, PipelineMixin, CachedFilesMixin, S3BotoStorage):
	pass

StaticRootS3BotoStorage = lambda **kwargs: S3PipelineStorage(
	location='static', **kwargs)


MediaRootS3BotoStorage  = lambda: S3BotoStorageCached(location='media')
