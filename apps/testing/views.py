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
    print("Response : ", json.dumps(response.json(), indent=4))
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
    print("Response : ", json.dumps(response.json(), indent=4))
    return response.json()


def get_error(response):
    formatted_error = json.dumps(
        json.loads(response.content.decode("utf-8")),
        indent=4
        )
    print(response.reason, ":", response.status_code)
    print(formatted_error)



## GET REQUESTS


def game_status():
    url = "https://api.spacetraders.io/v2"
    get_request(url)


def systems():
    url = "https://api.spacetraders.io/v2/systems"
    get_request(url)


def agent_info():
   ### Using global variables is a terrible idea ###
    global hq_location, home_system, symbol, account_id, credits
    url = "https://api.spacetraders.io/v2/my/agent"
    info = get_request(url)
    hq_location = info["data"]["headquarters"]
    home_system = hq_location[:7]
    symbol = info["data"]["symbol"]
    account_id = info["data"]["accountId"]
    credits = info["data"]["credits"]


def headquarters():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{hq_location}"
    except Exception:
        print("Error: Location details not set, try agent info")
        return
    get_request(url)


def list_own_ships():
    url = "https://api.spacetraders.io/v2/my/ships"
    get_request(url)


def list_contracts():
    ### No way to select different contracts 
    global contractId
    url = "https://api.spacetraders.io/v2/my/contracts"
    info = get_request(url)
    contractId = info["data"][0]["id"]


def detail_contract():
    try:
        url = f"https://api.spacetraders.io/v2/my/contracts/{contractId}"
    except NameError:
        print("Error: Contract details not set, try list contracts")
        return 
    get_request(url)


def list_waypoints():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except Exception:
        print("Error: Location details not set, try agent info")
        return
    get_request(url)


def detail_waypoint():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except:
        print("Error: Location details not set, try agent info")
        return
    get_request(url)


def find_shipyard():
    global shipyard, shipyard_system
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except Exception:
        print("Error: Location details not set, try agent info")
        return None
    
    info = get_request(url)
    data = info.get('data', [])

    for item in data:
        traits = item.get("traits", [])

        for trait in traits:
            if trait.get("symbol") == "SHIPYARD":
                shipyard = item.get('symbol',[])
                shipyard_system = shipyard[:7]
                print('Shipyard: ', shipyard)
                return shipyard, shipyard_system
             
    print('No shipyards found')
    return None


def list_ships():
    global ships_list, ships_dict
    try:
        url = f"https://api.spacetraders.io/v2/systems/{shipyard_system}/waypoints/{shipyard}/shipyard"
    except Exception:
        print("Error: Shipyard details not set, try find_shipyard")
        return None
    
    info = get_request(url)
    ships_list  = info['data']['shipTypes']
    ships_dict = {}
    for num , item in enumerate(ships_list):
        ships_dict[num + 1] = item['type']
    return ships_list


## POST REQUESTS


def purchase_ship():
    try:
        url = "https://api.spacetraders.io/v2/my/ships"
    except Exception:
        print("Error: Ship details not set, try list_ships")
        return
    
    print('From these choices:')
    for number, ship in ships_dict.items():
        print(f"{number}. {ship}")
    
    num_choice = input("Which number ship would you like? ")
    payload = {"shipType": ships_dict.get(int(num_choice)), "waypointSymbol": shipyard}
    
    post_request(url, payload)


def accept_contract():
    try:
        url = f"https://api.spacetraders.io/v2/my/contracts/{contractId}/accept"
    except Exception:
        print("Error: Contract details not set, try list contracts")
        return 
    
    payload = {}
    post_request(url, payload)
