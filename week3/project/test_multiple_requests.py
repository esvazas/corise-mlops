import json
import requests

headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

def get_test_json():
    with open('./data/requests.json', 'rb') as r:
        request_list = [json.loads(line) for line in r.readlines()]
    
    return request_list

def test_requests():
    for req_json in get_test_json():
        requests.post('http://0.0.0.0:80/predict', headers=headers, json=req_json)


if __name__ == '__main__':
    test_requests()