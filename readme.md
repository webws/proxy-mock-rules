Translations: [English](readme.md) | [简体中文](readme_zh.md) 
### Custom Script Rules for API Mocking with mimtproxy

## Usage
### Configuration Rules
* `rule.json` is a fixed JSON configuration file, as shown below:
```json
[
  {
    "url_pattern": "^http://127.0.0.1:1323/proxy-test.*$",
    "rewrite_rules": {
      "request_header": "kv_replace",
      "request_body": "kv_replace",
      "response_header": "kv_replace",
      "response_body": "full_rewrite"
    },
    "break_rlow": false,
    "mock_res_json_file": "mock_res.json"
  }
]
```
* `mock_res_json_file` is a JSON file that represents the mock response, as shown below:
``` json
{
  "status": 200,
  "header": {
    "Content-Type": "application/json; charset=UTF-8",
    "content-res": "res",
    "test": "dididi"
  },
  "content": {
    "value": "test",
    "key": "one"
  }
}
```
This configuration mocks the API at `http://127.0.0.1:1323/proxy-test` and responds body with the fixed JSON  shown above.
```json
{
    "value": "test",
    "key": "one"
  }

```

### Starting mitmproxy
Note: You need to install mitmproxy first.

```bash
mitmdump -p 8888 rule.py
```

## Example of Testing HTTP Mocking
Start a test HTTP server with the route `http://127.0.0.1:1323/proxy-test`. Without enabling the proxy, accessing this endpoint will return the following JSON response:
``` json
{"message":"Proxy test success!"}
```
After enabling the proxy and accessing the same endpoint, the response will be as follows:
``` json
{
    "value": "test",
    "key": "one"
}
```

Example of starting the server:
```bash
python3 ./test.py --server-start
```
### Sending a Request without Enabling the Proxy
```
❯ python3 ./test.py --client-query                                                                
{"message":"Proxy test success!"} 

```
### Sending a Request with the Proxy Enabled
The response will be the content from `mock_res.json`.
```bash
❯ python3 ./test.py --client-query --proxy 127.0.0.1:8888                                         
{"value": "test", "key": "one"}
```

### rewrite rules
TODO