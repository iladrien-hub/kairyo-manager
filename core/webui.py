from enum import Enum
from typing import Optional, Callable

import aiohttp
import ujson
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class HttpBackend(Enum):
    Asyncio = 1
    Qt = 2


class QtRequestProxy:

    def __init__(self, method: str, url: str, json: Optional[dict] = None):
        self.json = json
        self.url = url
        self.method = method

        self._nam: Optional[QNetworkAccessManager] = None

    def connect(self, parent: QObject, handler: Callable):
        self._nam = QNetworkAccessManager(parent)
        self._nam.finished.connect(handler)  # noqa

        return self

    def perform(self):
        req = QNetworkRequest(QUrl(self.url))

        method = getattr(self._nam, self.method.lower())
        if self.json is not None:
            req.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')
            method(req, ujson.dumps(self.json).encode('utf-8'))
        else:
            method(req)


class WebuiApi(object):
    def __init__(self, url: str, backend: HttpBackend = HttpBackend.Asyncio):
        while url.endswith('/'):
            url = url[:-1]
        self.url = url

        self._backend = backend

    async def _async_request(self, method: str, path: str, json: Optional[dict] = None):
        async with aiohttp.request(method, f'{self.url}{path}', json=json) as req:
            return await req.json()

    def _request(self, method: str, path: str, json: Optional[dict] = None):
        match self._backend:
            case HttpBackend.Asyncio:
                return self._async_request(method, path, json)
            case HttpBackend.Qt:
                return QtRequestProxy(method, f'{self.url}{path}', json)
            case _:
                raise ValueError(f'unknown http backend: {self._backend}')

    def txt2img(self, params):
        return self._request('POST', '/sdapi/v1/txt2img', json=params)

    def interrupt(self):
        return self._request('POST', '/sdapi/v1/interrupt')

    def progress(self):
        return self._request('GET', '/sdapi/v1/progress')

    def upscalers(self):
        return self._request('GET', '/sdapi/v1/upscalers')
