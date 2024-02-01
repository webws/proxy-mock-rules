import sys
from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

@app.route('/proxy-test', methods=['POST'])
def proxy_test():
    return jsonify({"message": "Proxy test success!"})

def start_server():
    app.run(port=1323)

def client_query(proxy_address=None):
    proxies = {}
    
    if proxy_address:
        proxies = {
            'http': f'http://{proxy_address}',
            'https': f'http://{proxy_address}',
        }
    
    response = requests.post('http://127.0.0.1:1323/proxy-test', proxies=proxies)
    print(response.text)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == '--server-start':
            server_thread = threading.Thread(target=start_server)
            server_thread.start()
            server_thread.join()
        elif command == '--client-query':
            proxy_arg = None
            if '--proxy' in sys.argv:
                try:
                    proxy_index = sys.argv.index('--proxy') + 1
                    proxy_arg = sys.argv[proxy_index]
                except IndexError:
                    print("Proxy address not specified after --proxy")
                    sys.exit(1)
            client_query(proxy_arg)
        else:
            print("Invalid command")
            sys.exit(1)
    else:
        print("Please provide a command argument")
        sys.exit(1)

