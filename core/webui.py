from typing import Optional

import aiohttp


class WebuiApi(object):
    def __init__(self, url: str):
        while url.endswith('/'):
            url = url[:-1]
        self.url = url

    async def _request(self, method: str, path: str, json: Optional[dict] = None):
        async with aiohttp.request(method, f'{self.url}{path}', json=json) as req:
            return await req.json()

    def txt2img(self, params):
        return self._request('POST', '/sdapi/v1/txt2img', json=params)

    def interrupt(self):
        return self._request('POST', '/sdapi/v1/interrupt')

    def progress(self):
        return self._request('GET', '/sdapi/v1/progress')
