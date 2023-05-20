from django.shortcuts import render
from datetime import datetime
from environ import Env; env = Env()
import json, requests, time, traceback
from sys import exit

def start_up():
    agent_info()
    list_own_ships()
    ship_status()
    navigate_ship()


def get_request(url):
    headers = {"Accept": "application/json",
                "Authorization": env("BEARER")
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        get_error(response)
        return None
    
    return response.json()


def post_request(url, payload, exp_status):
    headers = {"Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": env("BEARER")
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != exp_status:
        get_error(response)
        return None
    
    return response.json()


def get_error(response):
    formatted_error = json.loads(response.content.decode("utf-8"))
    error_message = formatted_error["error"]["message"]
    print("\n", error_message, sep="")
    return


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
            print("Please try again, enter 'yes' or 'no'.")


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
            print("Invalid input")



#########################              Basic Status              ###############################


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


def list_own_ships():
    global ship_symbol
    url = "https://api.spacetraders.io/v2/my/ships"
    info = get_request(url)
    ship_symbol = info['data'][0]['symbol']
    return


def ship_status():
    global ship_symbol, cargo_obj
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"
    except NameError:
        return None
    
    status_info = get_request(url)

    ship_name = status_info['data']['registration']['name']
    ship_role = status_info['data']['registration']['role']
    print(' ')
    print(ship_name, '/ Role:', ship_role)
    
    status = status_info['data']['nav']['status']
    flightmode = status_info['data']['nav']['flightMode']
    location = status_info['data']['nav']['route']['destination']['symbol']
    location_type = status_info['data']['nav']['route']['destination']['type']
    print('Location :', location_type, "-", location)
    print('Status :', status, "-", flightmode)

    fuel_capacity = status_info['data']['fuel']['capacity']
    fuel_current = status_info['data']['fuel']['current']
    fuel_index = fuel_current/fuel_capacity
    percentage_format("\nFuel", fuel_index)

    cargo_capacity = status_info['data']['cargo']['capacity']
    cargo_current = status_info['data']['cargo']['units']
    cargo_index = cargo_current/cargo_capacity
    cargo_obj = {}
    percentage_format("Cargo fill", cargo_index)

    print("\nCurrent cargo on", ship_name, ":\n")
    for goods in status_info['data']['cargo']['inventory']:
        goods_name = goods['symbol']
        amount = goods['units']
        print(goods_name,'-', amount)
        cargo_obj.update({goods_name:amount})
    return  


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


#########################              Purchasing ships              ###############################


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
    
    num_choice = input("Which numbered ship would you want? ")
    payload = {"shipType": ships_obj.get(int(num_choice)), "waypointSymbol": shipyard}
    exp_status = 201
    
    post_request(url, payload, exp_status)


#########################              Extraction             ###############################


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


def extract():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
        exp_status = 201
        payload = {}
        extract_info = post_request(url, payload, exp_status)
        detailed_extraction_info(extract_info)

    except NameError:
        print("\nName 'ship_symbol' is not defined, run start_up()") 
        return None


def detailed_extraction_info(extract_info):
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


#########################              Contracts             ###############################


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
        return None
    get_request(url)


def accept_contract():
    try:
        url = f"https://api.spacetraders.io/v2/my/contracts/{contractId}/accept"
    except NameError:   
        return None
    
    payload = {}
    exp_status = 200
    post_request(url, payload, exp_status)


#########################              Navigation             ###############################


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
        exp_status = 200
        navigate_info = post_request(url, payload, exp_status)
        arrival_in = detailed_navigate_info(navigate_info) 
        dock_choice(arrival_in, ship_symbol, payload)

    except NameError:
        traceback.print_exc()
        return None
    
    
#########################              Docking             ###############################

def docking():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/dock"
        payload = {}
        exp_status = 201

        post_request(url, payload, exp_status)
        refuel_choice(ship_symbol)

    except NameError:
        traceback.print_exc() 
        return None
    

def dock_choice(arrival_in, ship_symbol, payload):
    dock_choice = "\nShould we dock at our destination?\n"
    proceed = get_yes_no_input(dock_choice)

    try:
        if proceed:
            print("\nDocking on arrival, in c.", arrival_in, "secs\n" )
            time.sleep(arrival_in)
            docking(ship_symbol, payload)
        else:
            print("\nYou can also chooose on arrival, in c.",arrival_in,"secs\n")
            return
        
    except NameError:
        return None


#########################              Orbiting/Refueling            ###############################


def orbit():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/orbit"
        exp_status = 200
        payload = {}
        post_request(url, payload, exp_status)

    except NameError: 
        return None


def refuel():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/refuel"
        payload = {}
        post_request(url, payload)

    except NameError: 
        return None


def refuel_choice(ship_symbol):
    refuel_choice = "\nShould we refuel?\n"
    proceed = get_yes_no_input(refuel_choice)

    try:
        if proceed:
            print("\nRefueling now\n" )
            refuel(ship_symbol)
        else:
            print("\nSuit yourself\n")
            return 
        
    except NameError:
        return None



#########################              Selling cargo           ###############################


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


def cargo_choice():
    quick_choice = {}
    print("\nFrom these choices:")
    for index, cargo_type in enumerate(cargo_obj.keys(), start=1):
        print(f"{index}. {cargo_type}")
        quick_choice.update({index:cargo_type})

    question = "\nWhich numbered cargo to sell?\n"
    choice = num_choice(question)
    cargo_choice = quick_choice.get(choice)
    units = cargo_obj.get(cargo_choice, [])
    return cargo_choice, units


def sell_cargo():
    try:
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/sell"
    except NameError:   
        return None
    
    chosen, units = cargo_choice()
    payload = {"symbol": chosen, "units": units}
    exp_status = 201
    response = post_request(url, payload, exp_status)
    if response is not None:
        cargo_obj[chosen] = [] 
    return