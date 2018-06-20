"""
Shortlived async helpers. Primary target is creating short-lived fast context with get_context
"""

import os
from functools import lru_cache

from fan.context import AsyncContext
from fan.contrib.aio.discovery import LazyAiozkDiscovery
from fan.sync import get_tracer
from fan.transport import AsyncHTTPTransport, HTTPPropagator, DjangoPropagator


@lru_cache(maxsize=None)
async def get_discovery(is_django=False, name=None, loop=None):
    discovery = LazyAiozkDiscovery(
        os.environ.get('ZK_HOST', 'zk'),
        os.environ.get('ZK_CHROOT', '/'),
        with_data_watcher=False,
        loop=loop
    )
    discovery.transport_classes = {
        'http': AsyncHTTPTransport,
    }

    if not name and is_django:
        name = 'django'

    discovery.tracer = get_tracer(name)
    if is_django:
        discovery.tracer.register_propagator('http', DjangoPropagator())
    else:
        discovery.tracer.register_propagator('http', HTTPPropagator())
    return discovery


async def get_context(name=None, service_name=None, loop=None):
    if not service_name and name:
        service_name = name
    discovery = await get_discovery(is_django=False, name=service_name, loop=loop)
    return AsyncContext(discovery, name=name)