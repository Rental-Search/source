from django.utils.functional import SimpleLazyObject
from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin

from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
from boto.utils import parse_ts

class S3PipelineStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):
	pass
	

StaticRootS3BotoStorage = lambda **kwargs: S3PipelineStorage(
	location='static', **kwargs)