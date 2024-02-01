import json
import re
import logging
from typing import Optional, List, Union
from mitmproxy import http
import copy
from mitmproxy.test import tflow

logging.basicConfig(level=logging.INFO,
format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Rule:
    def __init__(self, config):
        self.url_pattern = config['url_pattern']
        self.mockLocalFileResJson = None
        self.mockLocalFileReqJson = None
        self.breakFlow = config.get('break_rlow', False)
        if 'mock_res_json_file' in config:
            with open(config['mock_res_json_file'], 'r') as f:
                self.mockLocalFileResJson = json.load(f)
        if 'mock_req_json_file' in config:
            with open(config['mock_req_json_file'], 'r') as f:
                self.mockLocalFileReqJson = json.load(f)
        self.rewriteRuleMap = config.get('rewrite_rules')

    def match(self, url):
        return re.match(self.url_pattern, url) is not None

    def print_attr(self):
        for key, value in vars(self).items():
            print(f'{key}: {value}')

    def full_rewrite_header(self, http_data: Union[http.Request, http.Response], oldMockJson):
        mockJson = copy.deepcopy(oldMockJson)
        if "header" in mockJson:
            new_headers = http.Headers()
            for key, value in mockJson["header"].items():
                new_headers[key] = value
            http_data.headers = new_headers

    def kv_replace_body(self, http_data: Union[http.Request, http.Response], oldMockJson):
        mockJson = copy.deepcopy(oldMockJson)
        if "content" in mockJson:
            try:
                bodyJson = http_data.json()
            except json.JSONDecodeError as e:
                logging.error("json decode error: %s", e)
                bodyJson = {}

            for key, value in mockJson["content"].items():
                bodyJson[key] = value
            http_data.text = json.dumps(bodyJson)

    def kv_replace_header(self, http_data: Union[http.Request, http.Response], oldMockJson):
        mockJson = copy.deepcopy(oldMockJson)
        if "header" in mockJson:
            http_data.headers.update(mockJson["header"])
        return

    def full_rewrite_body(self, http_data: Union[http.Request, http.Response], oldMockJson):
        if "content" in oldMockJson:
            mockJson = copy.deepcopy(oldMockJson)
            http_data.text = json.dumps(mockJson["content"])
        return

    def rewrite_data(self, flow: http.HTTPFlow, phase: str):
        logging.warn("rewrite_data phase: %s", phase)
        if self.breakFlow:
            logging.warn("break========================== flow")
            flow.response = http.Response.make(self.mockLocalFileResJson["status"],
                                               json.dumps(self.mockLocalFileResJson["content"]), self.mockLocalFileResJson["header"])

            return
        oldMockJson = self.mockLocalFileReqJson if phase == "request" else self.mockLocalFileResJson
        http_data = flow.request if phase == "request" else flow.response
        if not self.rewriteRuleMap:
            return
        for rewriteTarget, rewriteRule in self.rewriteRuleMap.items():
            if phase in rewriteTarget:
                method_suffix = rewriteTarget.split(phase)[1]
                method_name = rewriteRule + method_suffix
                logging.info(f"method_name: {method_name}")
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(http_data, oldMockJson)


rules: List[Optional[Rule]] = []


def load_rules(config_file_path):
    with open(config_file_path, 'r') as f:
        config_list = json.load(f)
    global rules
    for config in config_list:
        rules.append(Rule(config))

    for index in range(len(rules)):
        print(f"====global rule {index} ====")
        rules[index].print_attr()


config_file = 'rule.json'
load_rules(config_file)


def process_request(url) -> Optional[Rule]:
    for rule in rules:
        if rule.match(url):
            return rule
    return None


def request(flow: http.HTTPFlow) -> None:
    # return
    rule = process_request(flow.request.url)
    if rule is None:
        return
    rule.rewrite_data(flow, "request")


def response(flow: http.HTTPFlow) -> None:
    rule = process_request(flow.request.url)
    if rule is None:
        return
    rule.rewrite_data(flow, "response")


if __name__ == "__main__":
    test_url = "http://localhost:1323/proxy-test"
    f = tflow.tflow(resp=True)
    f.request.url = test_url
    f.request.headers = {"debug_req_header": "test"}
    f.request.text = '{"debug_req_text": "test"}'
    f.response.headers["debug_res_header"] = "test"
    f.response.text = '{"debug_res_text": "test"}'
    logging.info(
        "before request request.headers:%s, request.text:%s , response.headers:%s, response.text:%s",
        f.request.headers, f.request.text, f.response.headers, f.response.text)
    request(f)
    response(f)
    logging.info(
        f"after ======request header: {f.request.headers}, request body: {f.request.text}, response header: {f.response.headers}, response body: {f.response.text}"
    )
