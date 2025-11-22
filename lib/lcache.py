import os
import binascii


from lib.settings import Config
from lib.utils import singleton

_config = Config().get()


@singleton
class LocalCache:
    def __init__(self):
        if not os.path.exists(_config.local_cache.cache_dir):
            os.mkdir(_config.local_cache.cache_dir)

        self.loaded = {}

    def __contains__(self, item: str) -> bool:
        return (self.hexlify(item) + '.png') in os.listdir(_config.local_cache.cache_dir)
    
    def hexlify(self, item: str) -> str:
        return binascii.hexlify(item.encode("ascii")).decode("ascii")

    def get(self, url: str) -> bytes | None:
        name = self.hexlify(url) + '.png'
        
        if name not in self.loaded and name not in os.listdir(_config.local_cache.cache_dir):
            return
        
        if name in self.loaded:
            return self.loaded[name]
        
        img = open(os.path.join(_config.local_cache.cache_dir, name), 'rb').read()
        self.loaded[name] = img

        return img
    
    def set(self, url: str, img: bytes) -> None:
        if not _config.local_cache.caching:
            return

        name = self.hexlify(url) + '.png'
        self.loaded[name] = img
        
        with open(os.path.join(_config.local_cache.cache_dir, name), 'wb') as file:
            file.write(img)
