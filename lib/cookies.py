from aiohttp import ClientResponse


class Cookie(str):
    @staticmethod
    def _parse_string(string: str) -> dict:
        string = string.strip("\"")
        data = {}

        for pair in string.split("; "):
            data[pair[:pair.find("=")]] = pair[pair.find("=") + 1:]

        return data

    def __init__(self, cookies: str | dict):
        if isinstance(cookies, dict):
            self.data = cookies
        else:
            self.data = self._parse_string(cookies)
    
    def __str__(self):
        return '"' + '; '.join(f"{key}={value}" for key, value in self.data.items()) + '"'
    
    def __getitem__(self, key: str) -> str:
        return self.data[key]
    
    def __setitem__(self, key: str, value):
        self.data[key] = value

    def update_saved(self):
        if not self.data:
            return

        with open(".env", encoding="utf-8") as file:
            env_text = file.readlines()

        for i in range(len(env_text)):
            if env_text[i].startswith("Cookie="):
                env_text[i] = f"Cookie={self}" + ('\n' * env_text[i].endswith('\n'))
            break

        with open(".env", 'w', encoding='utf-8') as file:
            file.writelines(env_text)
    
    def get(self, key: str) -> str:
        return self.data.get(key)
    
    def set(self, key: str, value: str) -> None:
        self.data[key] = value

    def update(self, responce: ClientResponse) -> None:
        for head_name, head_value in responce.headers.items():
            if head_value and head_name == "Set-Cookie":
                key, value = head_value[:head_value.find("=")], head_value[head_value.find("=") + 1:head_value.find(";")]
                if value:
                    self[key] = value
