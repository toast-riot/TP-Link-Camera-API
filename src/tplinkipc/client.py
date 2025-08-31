import requests
from . import errors
from . import crypt
from . import request_session
from json import JSONDecodeError

class TPLinkIPCClient():
    def __init__(self, base_url: str, username: str, password: str):
        # these are the magic values from the original camera code. They might vary between devices or models, I don't know
        self._ENTRY_PASSWORD_TYPE = {"default": "1", "rsa": "2"} # original: entrypType
        self._PASSWORD_SALT = "TPCQ75NF2Y:" # from original: class.js > Tool.md5AuthPwd
        self._PASSWORD_TYPE = "md5" # original: entrypType

        self.base_url = base_url
        self._username = username
        self._password = password
        self._session_token = None
        self._req_session = request_session.unsafe_session
    
    def _log(self, message: str) -> None:
        print(f"[TPLinkIPCClient] ({self.base_url}) {message}")

    def _post(self, url: str, **kwargs) -> requests.Response:
        return self._req_session.post(f"{self.base_url}{url}", **kwargs, verify=False)

    def _get_auth_encrypt_type(self, encrypt_type: list) -> str: # original: getAuthEncryptType
        if isinstance(encrypt_type, list) and self._ENTRY_PASSWORD_TYPE["rsa"] in encrypt_type:
            return self._ENTRY_PASSWORD_TYPE["rsa"]
        return self._ENTRY_PASSWORD_TYPE["default"]
    
    class Method:
        GET = "get"
        SET = "set"
        DO = "do"

    def api_request(self, method: Method, payload: dict, allow_retry=True) -> str:
        if not self._session_token: self.login()
        payload["method"] = method

        resp = self._post(f"/stok={self._session_token}/ds", json=payload)
        if resp.status_code == 401:
            if not allow_retry:
                raise errors.SessionExpiredError(f"Session expired for {self.base_url}, please re-authenticate")
            self._log("Session expired, re-authenticating...")
            self._session_token = None
            return self.api_request(method, payload, allow_retry=False)

        if not resp.ok:
            self._log(f"API request failed with status code {resp.status_code}: {resp.text}")
            return None
        
        try: resp_json = resp.json()
        except JSONDecodeError:
            self._log(f"Failed to decode JSON response: {resp.text}")
            return None

        if resp_json.get("error_code", 0) != 0:
            self._log(f"API request returned error code: {resp_json.get('error_code')}")
            return None
        
        self._log(f"API request successful: {resp.status_code}")
        return resp_json

    def _fetch_encryption_info(self) -> tuple[str, str, str]:
        # NOTE: for some reason this endpoint returns 401 even when working correctly

        # response also has:
        # passwdType | always "md5" in my case
        # code       | can be various values, I haven't looked into it. I think it might be `-40{http code}`, e.g. -40401 for 401

        payload = {
            "method": "do",
            "user_management": {"get_encrypt_info": None}
        }
        resp = self._post("/", json=payload)
        if not (resp.ok or resp.status_code == 401):
            raise errors.ConnectionError(f"Failed to fetch encryption info for {self.base_url}: status code {resp.status_code}")
        data = resp.json()["data"]

        return (
            crypt.make_pem(requests.utils.unquote(data["key"])),
            data["nonce"],
            self._get_auth_encrypt_type(data["encrypt_type"])
        )

    def login(self) -> None:
        self._log(f"Logging in as {self._username}")
        pubkey_pem, nonce, encrypt_type = self._fetch_encryption_info()
        pwd_md5 = crypt.md5_auth_pwd(self._password, self._PASSWORD_SALT)
        if encrypt_type == self._ENTRY_PASSWORD_TYPE["rsa"]:
            encrypted_pwd = crypt.rsa_encrypt(f"{pwd_md5}:{nonce}", pubkey_pem)
        else:
            encrypted_pwd = pwd_md5

        payload = {
            "method": "do",
            "login": {
                "username": self._username,
                "password": requests.utils.quote(encrypted_pwd),
                "passwdType": self._PASSWORD_TYPE, # this is baked into the original login code, so I've baked it here too
                "encrypt_type": encrypt_type
            }
        }

        resp = self._post("/", json=payload)
        result = resp.json()
        if resp.ok and result.get("error_code") == 0 and (session_token := result["stok"]):
            self._session_token = session_token
        else:
            raise errors.LoginError(f"Status code {resp.status_code}, error code {result.get('error_code', 'Unknown error')}")