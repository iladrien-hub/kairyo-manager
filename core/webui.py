from typing import Optional

import aiohttp
import ujson
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class WebuiApi(object):
    def __init__(self, url: str, manager: QNetworkAccessManager = None):
        while url.endswith('/'):
            url = url[:-1]
        self.url = url

        self._manager = manager

    async def _async_request(self, method: str, path: str, json: Optional[dict] = None):
        async with aiohttp.request(method, f'{self.url}{path}', json=json) as req:
            return await req.json()

    def _qt_request(self, method: str, path: str, json: Optional[dict] = None):
        req = QNetworkRequest(QUrl(f'{self.url}{path}'))

        method = getattr(self._manager, method.lower())
        if json is not None:
            req.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')
            method(req, ujson.dumps(json).encode('utf-8'))
        else:
            method(req)

    def _request(self, method: str, path: str, json: Optional[dict] = None):
        if self._manager is None:
            return self._async_request(method, path, json)
        return self._qt_request(method, path, json)

    def txt2img(self, params):
        return self._request('POST', '/sdapi/v1/txt2img', json=params)

    def interrupt(self):
        return self._request('POST', '/sdapi/v1/interrupt')

    def progress(self):
        return self._request('GET', '/sdapi/v1/progress')

    def upscalers(self):
        return self._request('GET', '/sdapi/v1/upscalers')
