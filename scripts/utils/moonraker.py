import requests
import json

class Const:
    PRINTER_INFO_API_PATH = '/printer/info'
    SERVER_CONFIG_API_PATH = '/server/config'
    PRINTER_RESTART_API_PATH = '/printer/restart'
    SERVER_RESTART_API_PATH = '/server/restart'

class APIConnection(object):
    def __init__(self):
        self._url = 'http://localhost:80'

    @property
    def base_url(self):
        return self._url

    @base_url.setter
    def base_url(self, url):
        self._url = url

    @property
    def PrinterConnection(self):
        api_path = Const.PRINTER_INFO_API_PATH
        return requests.get(self.base_url + api_path)

    @property
    def ServerConfigConnection(self):
        api_path = Const.SERVER_CONFIG_API_PATH
        return requests.get(self.base_url + api_path)

class Moonraker():
    def __init__(self):
        self.connection = APIConnection()

    def get_config(self):
        result = {}
        result['printer'] = self.get_printer_config()
        result['server'] = self.get_server_config()

        return result
    def get_printer_config(self):
        result = self.connection.PrinterConnection

        if result.status_code != 200:
            print('Moonraker is not accessible at %s' % self.url)
            print('Received error code: %s' % result.status_code)
            print('Type in the correct URL below. You can also press enter to retry with the same URL or `q` to quit.')
            url = Input('URL (%s): ' % self.url)
            if url == 'q':
                sys.exit()
            elif len(url):
                self.url = url
                return self.get_printer_config()
            else:
                return self.get_printer_config()

        unloaded_config = result.text
        config = json.loads(unloaded_config)['result']
        self._printer_config = config
        return config

    def get_server_config(self):
        result = self.connection.ServerConfigConnection

        if result.status_code != 200:
            print('Moonraker is not accessible at %s' % self.url)
            print('Received error code: %s' % result.status_code)
            print('Type in the correct URL below. You can also press enter to retry with the same URL or `q` to quit.')
            url = Input('URL (%s): ' % self.url)
            if url == 'q':
                sys.exit()
            elif len(url):
                self.url = url
                return self.get_server_config()
            else:
                return self.get_server_config()

        unloaded_config = result.text
        config = json.loads(unloaded_config)['result']
        self._printer_config = config
        return config

    def RestartMoonraker(self):
        url = self.connection.base_url + Const.SERVER_RESTART_API_PATH
        requests.post(url)
        return

    def RestartKlippy(self):
        url = self.connection.base_url + Const.PRINTER_RESTART_API_PATH
        requests.post(url)
        return