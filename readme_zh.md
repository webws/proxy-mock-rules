Translations: [English](readme.md) | [简体中文](readme_zh.md)

## 基于 mimtproxy 自定义脚本.实现通用的 api mock 规则

## 使用
### 配置规则
* rule.json 为固定json配置文件,示例如下
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
* mock_res_json_file 示例如下
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
代表对 接口 http://127.0.0.1:1323/proxy-test 进行mock,响应body固定为
``` json
{
    "value": "test",
    "key": "one"
}
```
其他重写规则 在后面详细介绍
### 启动 mitmproxy 
ps:需要先安装 mitmproxy

```bash
mitmdump -p 8888 rule.py
```

## 测试http mock示例
启动一个测试http服务,路由为 http://127.0.0.1:1323/proxy-test,不启动代理的情况下,访问该接口,返回如下
``` json
{"message":"Proxy test success!"}
```
启动代理后,访问该接口,返回如下
``` json
{
    "value": "test",
    "key": "one"
}
```

示例启动服务
```bash
python3 ./test.py --server-start
```
### 发起请求,不启动代理
```
❯ python3 ./test.py --client-query                                                                
{"message":"Proxy test success!"} 

```
### 发起请求,启动代理
响应为mock_res.json中的content
```bash
❯ python3 ./test.py --client-query --proxy 127.0.0.1:8888                                         
{"value": "test", "key": "one"}
```

## 重写规则
TODO