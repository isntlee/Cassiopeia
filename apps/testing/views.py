from django.shortcuts import render
from environ import Env; env = Env()
import json, requests


def get_request(url):
    headers = {"Accept": "application/json",
                "Authorization": env("BEARER")
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        get_error(response)
        return
    print("RESPONSE : ", response.json())
    print(json.dumps(response.json(), indent=4))
    return response.json()


def post_request(url, payload):
    headers = {"Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": env("BEARER")
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        get_error(response)
        return
    print("RESPONSE : ", response.json())
    print(json.dumps(response.json(), indent=4))


def get_error(response):
    formatted_error = json.dumps(json.loads(response.content.decode("utf-8")), indent=4)
    print(response.reason, ":", response.status_code)
    print(formatted_error)


# GET REQUESTS


def game_status():
    url = "https://api.spacetraders.io/v2"
    get_request(url)


def my_agent():
    url = "https://api.spacetraders.io/v2/my/agent"
    get_request(url)


def systems():
    url = "https://api.spacetraders.io/v2/systems"
    get_request(url)


# # POST REQUESTS


def purchase_ship():
    url = "https://api.spacetraders.io/v2/my/ships"
    payload = {"shipType": "SHIP_PROBE", "waypointSymbol": "string"}
    post_request(url, payload)
