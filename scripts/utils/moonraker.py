import requests
import json

class APIConnection(object):
    def __init__(self):
        self._url = 'http://localhost:80'
        self._api_path = '/printer/info'

    @property
    def base_url(self):
        return self._url

    @base_url.setter
    def base_url(self, url):
        self._url = url

    @property
    def api_path(self):
        return self._api_path

    @api_path.setter
    def api_path(self, path):
        self._api_path = path

    @property
    def url(self):
        return self._url + self._api_path

    def Connect(self):
        return requests.get(self.url)

class Moonraker():
    def __init__(self):
        self.connection = APIConnection()
    def get_config(self):
        print('Getting config....')
        result = self.connection.Connect()

        if result.status_code != 200:
            print('Moonraker is not accessible at %s' % self.url)
            print('Received error code: %s' % result.status_code)
            print('Type in the correct URL below. You can also press enter to retry with the same URL or `q` to quit.')
            url = Input('URL (%s): ' % self.url)
            if url == 'q':
                sys.exit()
            elif len(url):
                self.url = url
                return self.get_config()
            else:
                return self.get_config()

        unloaded_config = result.text
        config = json.loads(unloaded_config)['result']
        self.config = config
        return config
