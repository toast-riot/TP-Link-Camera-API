import ssl
import urllib3
from urllib3.poolmanager import PoolManager
import requests
from requests.adapters import HTTPAdapter

def _get_unsafe_session():
    session = requests.Session()
    session.mount("https://", _UnsafeTLSAdapter())
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return session

class _UnsafeTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        # ctx.set_ciphers('ALL:@SECLEVEL=0') # if it isn't working, try this
        ctx.set_ciphers('AES256-GCM-SHA384')
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx,
            **pool_kwargs
        )

unsafe_session = _get_unsafe_session()