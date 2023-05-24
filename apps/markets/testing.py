import json, time, traceback
from datetime import datetime
from sys import exit

import requests
from requests.exceptions import HTTPError

from django.shortcuts import render
from environ import Env; env = Env()


def start_up():
    agent_info()
    list_own_ships()


def get_request(url):
    headers = {"Accept": "application/json",
                "Authorization": env("BEARER")
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    return response.json()


def post_request(url, payload):
    headers = {"Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": env("BEARER")
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    return response.json()


def get_error(response):
    global error_message
    formatted_error = json.loads(response.content.decode("utf-8"))
    error_message = formatted_error["error"]["message"]
    print("\n", error_message, sep="")
    return error_message


def percentage_format(name, index):
    formatted_index = "{:.2%}".format(index)
    print(f"{name}:", formatted_index)
    return


def get_yes_no_input(prompt):
    while True:
        choice = input(prompt).lower()
        if choice in ['yes', 'y', 'ye']:
            return True
        elif choice in ['no', 'n']:
            return False
        elif choice == 'quit':
            exit()
        else:
            print("Please enter 'yes', 'no' or 'quit'")


def num_choice(question):
    choice = None
    while choice != "quit":
        choice = input(question)
        
        if choice.isdigit():
            choice = int(choice)
            return choice  
        elif choice.lower() == "quit":
            exit()
        else:
            print("Please enter a number or 'quit'")



#########################              Basic Status    (USER)          ###############################


def game_status():
    url = "https://api.spacetraders.io/v2"
    get_request(url)


def systems():
    url = "https://api.spacetraders.io/v2/systems"
    get_request(url)


def headquarters():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{hq_location}"
    except NameError:
        return None
    get_request(url)


def agent_info():
    global hq_location, home_system, symbol, account_id, credits
    url = "https://api.spacetraders.io/v2/my/agent"
    info = get_request(url)
    hq_location = info["data"]["headquarters"]
    home_system = hq_location[:7]
    symbol = info["data"]["symbol"]
    account_id = info["data"]["accountId"]
    credits = info["data"]["credits"]
    return hq_location, home_system,'HOME'




#########################              Purchasing ships    (SHIPS)          ###############################


def change_ship():
    global ship_symbol
    n = int(ship_symbol[-1])
    if n < no_ships:
        n += 1
    elif n > 0:
        n -= 1
    changed_ship = ship_symbols[n-1]
    ship_symbol = changed_ship
    return changed_ship


def ship_status(ship_symbol):
    global cargo_index, cooldown, fuel_index
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"
    except NameError:
        return None
    
    status_info = get_request(url)
    time.sleep(1)
    ship_name = status_info['data']['registration']['name']
    ship_role = status_info['data']['registration']['role']
    print('\n\n')
    print(ship_name, '/ Role:', ship_role)
    
    status = status_info['data']['nav']['status']
    flightmode = status_info['data']['nav']['flightMode']
    location = status_info['data']['nav']['route']['destination']['symbol']
    location_type = status_info['data']['nav']['route']['destination']['type']
    print('Location :', location_type, "-", location)
    print('Status :', status, "-", flightmode)
    print('Credits:', credits)

    fuel_capacity = status_info['data']['fuel']['capacity']
    fuel_current = status_info['data']['fuel']['current']
    fuel_index = fuel_current/fuel_capacity
    percentage_format("\nFuel", fuel_index)

    cargo_capacity = status_info['data']['cargo']['capacity']
    cargo_current = status_info['data']['cargo']['units']
    cargo_index = cargo_current/cargo_capacity
    cooldown = 0
    percentage_format("Cargo fill", cargo_index)
    return 


def list_own_ships():
    global ship_symbol, no_ships, ship_symbols
    url = "https://api.spacetraders.io/v2/my/ships"
    info = get_request(url)
    ship_symbol = info['data'][0]['symbol']
    no_ships = info['meta']['total']
    ship_symbols = []
    for i in range(no_ships):
        n = i
        try:
            ship_symbols.append(info['data'][n]['symbol'])
        except IndexError:
            pass
    print("Ships: ", ship_symbols)
    return

def find_shipyard():
    global shipyard, shipyard_system
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except NameError:
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
    global ships_list, ships_obj
    try:
        url = f"https://api.spacetraders.io/v2/systems/{shipyard_system}/waypoints/{shipyard}/shipyard"
    except NameError:
        return None
    
    info = get_request(url)
    ships_list  = info['data']['shipTypes']
    ships_obj = {}
    for num , item in enumerate(ships_list):
        ships_obj[num + 1] = item['type']
    return ships_list


def purchase_ship():
    try:
        url = "https://api.spacetraders.io/v2/my/ships"
    except Exception:    
        return None
    
    print('From these choices:')
    for number, ship in ships_obj.items():
        print(f"{number}. {ship}")
    
    choice = num_choice("Which numbered ship would you want? ")
    payload = {"shipType": ships_obj.get(int(choice)), "waypointSymbol": shipyard}
    
    post_request(url, payload)


#########################              Extraction             ###############################


def extract(ship_symbol):
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
        payload = {}
        extract_info = post_request(url, payload)
        detailed_extraction_info(extract_info)

    except Exception:
        print("Error message:", error_message) 
        return None


def detailed_extraction_info(extract_info):
    global cargo_index, cooldown
    extr_material = extract_info['data']['extraction']['yield']['symbol']
    extr_amount = extract_info['data']['extraction']['yield']['units']
    cooldown = extract_info['data']['cooldown']['remainingSeconds']
    cargo_capacity = extract_info['data']['cargo']['capacity']
    cargo_current = extract_info['data']['cargo']['units']
    cargo_index = cargo_current/cargo_capacity
    extr_index = extr_amount/cargo_capacity
    print("\nCooldown:", cooldown, 'secs')
    print("Material:", extr_material,'- Amount:', extr_amount)
    percentage_format("Cargo fill", cargo_index)
    percentage_format("Last load", extr_index)
    return


#########################              Contracts    (FACTIONS)          ###############################


def list_contracts():
    global contractId
    url = "https://api.spacetraders.io/v2/my/contracts"
    info = get_request(url)
    contractId = info["data"][0]["id"]


def detail_contract():
    try:
        url = f"https://api.spacetraders.io/v2/my/contracts/{contractId}"
    except NameError:
        return None
    get_request(url)


def accept_contract():
    try:
        url = f"https://api.spacetraders.io/v2/my/contracts/{contractId}/accept"
    except NameError:   
        return None
    
    payload = {}
    post_request(url, payload)


#########################              Navigation             ###############################

def list_waypoints():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except NameError:
        return None
    get_request(url)


def detail_waypoint():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except NameError:
        return None
    get_request(url)


def find_asteroids():
    global asteroids, asteroids_system
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
    except NameError:
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
    global destinations_obj
    destinations_obj = {}
    info = agent_info()
    destinations_obj.update({info[2]:info[0]})
    info = find_asteroids()
    destinations_obj.update({info[2]:info[0]})
    return


def destination_choice():
    quick_choice = {}
    print("\nFrom these choices:")
    for index, destination_type in enumerate(destinations_obj.keys(), start=1):
        print(f"{index}. {destination_type}")
        quick_choice.update({index:destination_type})

    question = "\nWhich numbered destination is correct?\n"
    choice = num_choice(question)
    waypoint_name = quick_choice.get(choice)
    return waypoint_name


def detailed_navigate_info(navigate_info):
    fuel_capacity = navigate_info['data']['fuel']['capacity']
    fuel_current = navigate_info['data']['fuel']['current']
    fuel_index = fuel_current/fuel_capacity
    arrival_time = datetime.fromisoformat(navigate_info['data']['nav']['route']['arrival'])
    departure_time = datetime.fromisoformat(navigate_info['data']['nav']['route']['departureTime'])
    arrival_in = int((arrival_time-departure_time).seconds)
    percentage_format("\nFuel", fuel_index)
    print('Arriving in :', arrival_in, 'secs')
    return (arrival_in)


def navigate_ship():
    global arrival_in, ship_symbol, payload, waypoint_name, waypoint
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/navigate"
    except NameError:
        return None
    
    if 'destinations' not in globals():
        find_destinations()

    try:
        waypoint_name = destination_choice()
        waypoint = destinations_obj.get(waypoint_name)
        payload = {"waypointSymbol": waypoint}
        navigate_info = post_request(url, payload)
        arrival_in = detailed_navigate_info(navigate_info) 
        dock_choice(arrival_in, ship_symbol, payload)

    except NameError:
        return None
    
    
#########################              (Logistics)             ###############################

def docking():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/dock"
        payload = {}

        post_request(url, payload)
        print("\nDocking now" )
        if fuel_index < 0.33:
            refuel()

    except NameError:
        return None
    

def dock_choice(arrival_in, ship_symbol, payload):
    dock_choice = "\nShould we dock at our destination?"
    proceed = get_yes_no_input(dock_choice)

    try:
        if proceed:
            print("\nDocking on arrival, in c.", arrival_in, "secs\n" )
            time.sleep(arrival_in)
            docking()
        else:
            print("\nYou can also chooose on arrival, in c.",arrival_in,"secs\n")
            return
        
    except NameError:
        return None


def orbit(ship_symbol):
    global orbit_bool
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/orbit"
        payload = {}
        post_request(url, payload)
        orbit_bool = True

    except NameError:
        print("\nError - in orbit, about to.. ? ")  
        return None


def refuel():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/refuel"
        payload = {}
        post_request(url, payload)

    except NameError: 
        return None


def refuel_choice(ship_symbol):
    refuel_choice = "\nShould we refuel?"
    proceed = get_yes_no_input(refuel_choice)

    try:
        if proceed:
            print("\nRefueling now" )
            refuel()
        else:
            print("\nSuit yourself")
            return 
        

        
    except NameError:
        return None



#########################              Selling cargo   (MARKET)        ###############################


def market_data():
    try:
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{waypoint}/market"
    except NameError:
        print('NameError, something in the request url is wrong')
        return None
    
    info = get_request(url)
    data = info.get('data', [])

    print("\nCurrent prices at", waypoint_name,"-", waypoint,"\n")
    for goods in data['tradeGoods']:
        goods_name = goods['symbol']
        sell_price = goods['sellPrice']
        print(goods_name,'-', float(sell_price))

    ("Would you like to make a sale?")         
    return None


def cargo_choice(cargo_obj):
    quick_choice = {}
    print("\nFrom these choices:")
    for index, cargo_type in enumerate(cargo_obj.keys(), start=1):
        print(f"{index}. {cargo_type}")
        quick_choice.update({index:cargo_type})

    # question = "\nWhich numbered cargo to sell?\n"
    # choice = num_choice(question)

    choice = 2
    cargo_choice = quick_choice.get(choice)
    units = cargo_obj.get(cargo_choice, [])
    return cargo_choice, units


def sell_cargo():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/sell"
    except NameError:   
        return None
    
    cargo_obj = cargo_status()
    chosen, units = cargo_choice(cargo_obj)
    payload = {"symbol": chosen, "units": units}
    response = post_request(url, payload)
    
    if response is not None:
        cargo_obj[chosen] = 0
        sale_choice(cargo_obj)


def sale_choice(cargo_obj):
    cargo_obj = cargo_status()

    if len(cargo_obj) > 1:
        sell_cargo()
        return
    else:
        return
    
    # proceed = get_yes_no_input(sale_choice)
    # cargo_status()
    # try:
    #     if proceed:
    #         sell_cargo()
    #     else:
    #         return   
    # except NameError:
    #     ("Error in sell cargo, sale choice")
    #     return None


def cargo_status():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"
    except NameError:
        return None
    status_info = get_request(url)
    cargo_obj = {}

    for goods in status_info['data']['cargo']['inventory']:
        goods_name = goods['symbol']
        amount = goods['units']
        cargo_obj.update({goods_name:amount})

    return cargo_obj


#########################              Final function/script        ###############################


def ending_script(): 

    start_up()
    time.sleep(1)
    ship_status(ship_symbol)
    time.sleep(1)
    orbit(ship_symbol)
    limit = float(0.95)

    while True:
        try:

            if cargo_index > limit: 
                try:
                    docking()
                    sell_cargo()
                    time.sleep(1)
                    ending_script()

                except Exception:
                    traceback.print_exc()
                    return
            
            else: 
                changed_ship = change_ship()
                ship_status(changed_ship)
                time.sleep(1)

                try:
                    orbit(changed_ship)
                    extract(changed_ship)
                    time.sleep(cooldown/2)

                except Exception:
                    traceback.print_exc()   

        except Exception:
            traceback.print_exc()
            

            