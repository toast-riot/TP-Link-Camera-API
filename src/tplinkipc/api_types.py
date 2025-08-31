class _PathHandler:
    @staticmethod
    def _set_data(path: tuple[str], value) -> dict:
        result = current = {}
        for el in path[:-1]:
            current[el] = {}
            current = current[el]
        current[path[-1]] = value
        return result

    @staticmethod
    def _get_data(path: tuple[str], value) -> dict:
        for el in path:
            if not isinstance(value, dict): return
            value = value.get(el)
        return value

    @staticmethod
    def _get_api(path: tuple[str]) -> dict:
        result = current = {}
        for el in path[:-1]:
            current[el] = {}
            current = current[el]
        current['name'] = path[-1]
        return result

class BasicValue:
    def __init__(self, client_attr_name: str, data_path: tuple[str], api_path: tuple[str]):
        self.client_attr_name = client_attr_name
        self.data_path = data_path
        self.api_path = api_path

    def __get__(self, obj, objtype=None):
        client = getattr(obj, self.client_attr_name)
        response = client.api_request(client.Method.GET, _PathHandler._get_api(self.api_path))
        if response: return _PathHandler._get_data(self.data_path, response)

    def __set__(self, obj, value):
        client = getattr(obj, self.client_attr_name)
        client.api_request(client.Method.SET, _PathHandler._set_data(self.data_path, value))