# TP-Link Camera API
A Python API for the configuration of TP-Link IP cameras.
Can be used to automate changing any setting of the camera that the camera's web UI shows (except user/password management).

> [!WARNING]
> This is a barebones API. If you want to add support for more of the camera's settings, you will need to use devtools to find the API paths to change those settings, then define them in [api.py](src/tplinkipc/api.py).

Tested with the TP-Link VIGI C350.

## Why
Because I thought it would be fun to reverse engineer the web UI's authentication flow. It turned out to be annoyingly easy, since the code is simple and not obfuscated. Regardless, I made it into a basic API in case someone wanted it.

## How it Works
It makes requests in the same way that the camera's web UI does, basically.

## The Authentication Flow
Documentation of how the authentication works.

### Inputs
| Field      | Description                          |
|------------|--------------------------------------|
| `base_url` | A (HTTPS) URL to the camera's web UI |
| `username` | The username for authentication      |
| `password` | The password for authentication      |

You also need a `salt` for RSA encryption. In my case, it was just hardcoded into the `class.js > Tool.md5AuthPwd` function.

---

### 1. Get Encryption Info
<sup>impl: `TPLinkIPCClient._fetch_encryption_info`</sup>

1. Send a POST request to `base_url`

   Body:
   ```python
   {
      "method": "do",
      "user_management": {
         "get_encrypt_info": None
      }
   }
   ```
   
   Response fields:
   | Field          | Type        | Description                                             |
   |----------------|-------------|---------------------------------------------------------|
   | `code`         | `int`       | An error code                                           |
   | `encrypt_type` | `list[str]` | The device's supported encryption types                 |
   | `key`          | `str`       | RSA public key for encrypting the password              |
   | `nonce`        | `str`       | A nonce value                                           |
   | `passwdType`   | `str`       | Always "md5" in my tests; not used by the web interface |

   > **Note:** This endpoint returns status code 401 and a non-zero `code` despite allowing access.

3. Un-URL-quote `key`, then convert to PEM format &#8594; `pubkey_pem`
4. Determine which encryption type to use from `encrypt_type` &#8594; `encrypt_type`

---

### 2. Prepare Password
<sup>impl: `TPLinkIPCClient.login`</sup>

1. MD5 hash `{password}{salt}` &#8594; `pwd_md5`
2. Encrypt password:
   - If `encrypt_type` is RSA:
      - RSA encrypt `{pwd_md5}:{nonce}` with key `pubkey_pem` &#8594; `encrypted_pwd`
   - Otherwise:
      - Use `pwd_md5` as `encrypted_pwd`
3. URL-quote `encrypted_pwd` &#8594; `encrypted_pwd`

---

### 3. Send Login Request
<sup>impl: `TPLinkIPCClient.login`</sup>

1. Send a POST request to `base_url`
   
   Body:
   ```python
   {
       "method": "do",
       "login": {
           "username": username,
           "password": encrypted_pwd,
           "passwdType": "md5",
           "encrypt_type": encrypt_type
       }
   }
   ```
   > **Note:** `"md5"` is hardcoded as `passwdType` because it was hardcoded in the web UI's code. Perhaps previous firmware versions used MD5 for authentication?

   Response fields:
   | Field        | Type  | Description       |
   |--------------|-------|-------------------|
   | `error_code` | `int` | An error code     |
   | `stok`       | `str` | The session token |

To use the token, send a request to `{base_url}/stok={stok}/ds` with whatever body is necessary to get or set the target setting.

---

## Notes
- My camera uses the [`TLS_RSA_WITH_AES_256_GCM_SHA384`](https://ciphersuite.info/cs/TLS_RSA_WITH_AES_256_GCM_SHA384) on TLS 1.2. I had to configure the code to use this cipher, as it was not permitted for TLS 1.2 by default (due to it being old).
- You can access an emulated web UI of some cameras [here](https://emulator.tp-link.com/vigi-ipc); though it doesn't emulate almost any of the web requests that this project relies on.
