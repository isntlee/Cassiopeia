from django.shortcuts import render
from datetime import datetime
from environ import Env; env = Env()
import json, requests, time


def get_request(url):
    headers = {"Accept": "application/json",
                "Authorization": env("BEARER")
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        get_error(response)
    # print("Response : ", json.dumps(response.json(), indent=4))
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
    # print("Response : ", json.dumps(response.json(), indent=4))
    return response.json()


def get_error(response):
    formatted_error = json.loads(response.content.decode("utf-8"))
    error_code = formatted_error["error"]["code"]

    print(response.reason, ":", response.status_code)
    print(formatted_error) 
    print('Error Code:', error_code)
    return error_code


def get_yes_no_input(prompt):
    while True:
        choice = input(prompt).lower()
        if choice in ['yes', 'y', 'ye']:
            return True
        elif choice in ['no', 'n']:
            return False
        else:
            print("Please try again, enter 'yes' or 'no'.")



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
    return hq_location, home_system,'HOME'


def headquarters():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{hq_location}"
    except Exception:
        print("Error: Location details not set, try agent info")
        return
    get_request(url)


def list_own_ships():
    global ship_symbol
    url = "https://api.spacetraders.io/v2/my/ships"
    info = get_request(url)
    ship_symbol = info['data'][0]['symbol']


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


def find_asteroids():
    global asteroids, asteroids_system
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except Exception:
        print("Error: Location details not set, try agent info")
        return None
    
    info = get_request(url)
    data = info.get('data', [])

    for item in data:
        if item.get("type") == "ASTEROID_FIELD":
            asteroids = item.get('symbol',[])
            asteroids_system = asteroids[:7]
            return asteroids, asteroids_system, "ASTEROID_FIELD"
             
    print('No asteroids found')
    return None


def find_destinations():
    global destinations
    destinations = {}
    info = agent_info()
    destinations.update({info[2]:info[0]})
    info = find_asteroids()
    destinations.update({info[2]:info[0]})
    navigate_ship()


def docking_destination(arrival_in, ship_symbol):
    time.sleep(arrival_in)
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/dock"
        post_request(url)
        
    except Exception:
        print("Error: Location details not set, try agent info") 
    


## POST REQUESTS


def navigate_ship():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/navigate"
    except Exception:
        print("Error: Ship details not set, try list_ships")
        return
    try:
        destinations
        try:
            print("\nFrom these choices:")
            quick_choice = {}
            for index, destination_type in enumerate(destinations.keys(), start=1):
                print(f"{index}. {destination_type}")
                quick_choice.update({index:destination_type})

            num_choice = int(input("\nWhich numbered destination is correct?\n"))
            waypoint = quick_choice.get(num_choice)
            payload = {"waypointSymbol": destinations.get(waypoint)}

            info = post_request(url, payload)
            fuel_capacity = info['data']['fuel']['capacity']
            fuel_current = info['data']['fuel']['current']
            fuel_index = fuel_current/fuel_capacity
            arrival_time = datetime.fromisoformat(info['data']['nav']['route']['arrival'])
            departure_time = datetime.fromisoformat(info['data']['nav']['route']['departureTime'])
            arrival_in = int((arrival_time-departure_time).seconds)

            print("\nFuel :", fuel_index)
            print('Arriving in :', arrival_in, 'secs')

            dock_choice = "\nShould we dock at our destination?\n"
            proceed = get_yes_no_input(dock_choice)

            if proceed:
                print("\nDocking on arrival\n")
                docking_destination(arrival_in, ship_symbol)
                return
            else:
                print("You can chooose on arrival")
                
        except Exception:

            ### This is still a real problem ###
            print('HERE WE ARE #1')
            pass

    except NameError:
        find_destinations()


def purchase_ship():
    try:
        url = "https://api.spacetraders.io/v2/my/ships"
    except Exception:
        print("Error: Ship details not set, try list_ships")
        return
    
    print('From these choices:')
    for number, ship in ships_dict.items():
        print(f"{number}. {ship}")
    
    num_choice = input("Which numbered ship would you want? ")
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
