"""
Backend for redis.

Requires redis.py from the redis source (found in client-libraries/python).
"""

from queues.backends.base import BaseQueue
from queues import InvalidBackend, QueueException
import os
import math

try:
    import redis
except ImportError:
    raise InvalidBackend("Unable to import redis.")

CONN = DB = None

try:
    from django.conf import settings
    CONN = getattr(settings, 'QUEUE_REDIS_CONNECTION', None)
    DB = getattr(settings, 'QUEUE_REDIS_DB', None)
    TIMEOUT = getattr(settings, 'QUEUE_REDIS_TIMEOUT', None)

except:
    CONN = os.environ.get('QUEUE_REDIS_CONNECTION', None)
    DB = os.environ.get('QUEUE_REDIS_DB', None)
    TIMEOUT = os.environ.get('QUEUE_REDIS_TIMEOUT', None)

if not CONN:
    raise InvalidBackend("QUEUE_REDIS_CONNECTION not set.")

try:
    from urlparse import urlparse
    redis_url = urlparse(CONN)
    host = redis_url.hostname
    port = redis_url.port
    password = redis_url.password
except ValueError:
    raise InvalidBackend("QUEUE_REDIS_CONNECTION should be in the format host:port (such as localhost:6379).")

try:
    port = int(port)
except ValueError:
    raise InvalidBackend("Port portion of QUEUE_REDIS_CONNECTION should be an integer.")


def _get_connection(host=host, port=port, db=DB, password=password, timeout=TIMEOUT):
    kwargs = {'host' : host, 'port' : port}
    if DB:
        kwargs['db'] = DB
    if timeout:
        kwargs['timeout'] = float(timeout)
    if password:
        kwargs['password'] = password
    try:
        # Try using the "official" redis kwargs
        return redis.Redis(**kwargs)
    except TypeError, e:
        # Possibly 'timeout' caused an issue...
        if 'timeout' not in kwargs:
            raise
        # Try using Andy McCurdy's library
        kwargs['socket_timeout'] = kwargs.pop('timeout')
        return redis.Redis(**kwargs)


class Queue(BaseQueue):
    def __init__(self, name, connection=None):
        try:
            self.name = name
            self.backend = 'redis'
            self._connection = connection or _get_connection()
        except redis.RedisError, e:
            raise QueueException, "%s" % e

    def read(self, block=False, timeout=0):
        try:
            if block:
                # Redis requires an integer, so round a float UP to the nearest
                # int (0.1 -> 1).
                try:
                    m = self._connection.blpop(self.name, timeout=int(math.ceil(timeout)))[1]
                except TypeError:
                    m = None
            else:
                m = self._connection.lpop(self.name)
            if m is None:
                raise QueueException('Queue is empty')
            return m
        except redis.RedisError, e:
            raise QueueException(str(e))

    def write(self, value):
        try:
            resp = self._connection.rpush(self.name, value)
            if resp in ('OK', 1):
                return True
            else:
                return False
        except redis.RedisError, e:
            raise QueueException, "%s" % e

    def __len__(self):
        try:
            return self._connection.llen(self.name)
        except redis.RedisError, e:
            raise QueueException, "%s" % e

    def __repr__(self):
        return "<Queue %s>" % self.name


def create_queue():
    """This isn't required, so we noop.  Kept here for swapability."""
    return True


def delete_queue(name):
    """Delete a queue"""
    try:
        resp = _get_connection().delete(name)
        if resp and resp == 1:
            return True
        else:
            return False
    except redis.RedisError, e:
        raise QueueException, "%s" % e


def get_list():
    return _get_connection().keys('*')
