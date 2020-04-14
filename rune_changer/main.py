import sys
import traceback
import requests
import base64
import json
import time
import re
import logging

from urllib3.exceptions import InsecureRequestWarning

from utils import runeforge, misc

from win10toast import ToastNotifier

notify = ToastNotifier()

logging.basicConfig(format='%(asctime)s:%(levelname)s::%(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def initialization():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.debug(e)
        logger.warning("Something went wrong while loading config. Probably syntax is wrong.")
        config = {}

    def get_basic_data():
        logger.info("Trying to fetch data from Lockfile.")
        try:
            path = config.get('lockfile_path', None) or "C:\Riot Games\League of Legends\League of Legends\lockfile"
            with open(path, 'r') as lockfile:
                text = lockfile.read()
        except FileNotFoundError:
            logger.error("Lockfile not found in base location. You need to specify path in config file.")
        else:
            config['lockfile_path'] = path

            _data = text.split(":")
            return _data


    global MAIN_INTERVAL
    MAIN_INTERVAL = config.get("interval", 5)

    data = get_basic_data()
    if not data:
        return None
    PORT = data[2]
    PASSWORD = base64.b64encode(f'riot:{data[3]}'.encode('ascii')).decode("utf-8")

    global URL
    URL = f"https://127.0.0.1:{PORT}"

    logger.info(f"Base data fetched: `PORT={PORT} PASSWORD={PASSWORD} URL={URL}`")

    global headers
    headers = {
      "Accept": "application/json",
      "Authorization": f"Basic {PASSWORD}"
    }

    global IGNORED
    IGNORED = ["LeBlanc"]

    url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json"
    r = requests.get(url)
    global champions
    champions = r.json()

    global champs_map
    champs_map = {
        "Cho'Gath": "Chogath",
        "Nunu & Willump": "Nunu",
        "Dr. Mundo": "DrMundo",
        "Kha'Zix": "Khazix",
        "Kog'Maw": "Kogmaw",
        "Rek'Sai": "Reksai",
    }

    try:
        with open("config.json", "w") as f:
            config = json.dump(config, f)
    except Exception as e:
        print(e)


def get_champion_by_id(key):
    try:
        return champs_map[key]
    except KeyError:
        for champ in champions:
            if champions[champ]["id"] == key:
                return champ


def _add_spaces(word):
    if word in IGNORED:
        return word
    return re.sub(r"(\w)([A-Z])", r"\1 \2", word)


def get_gameflow_session(debug):
    phase_url = "/lol-gameflow/v1/session"

    r = requests.get(URL + phase_url, headers=headers, verify=False)
    req = r.json()
    return req


def run_phase(*, debugger=None):

    debug = logger or debugger

    try:
        req = get_gameflow_session(debug)
    except Exception as e:
        debug.debug(e)
        debug.critical("Failed to fetch session. Probably game is already in progress or League client is not opened. Aborting.")
        return MAIN_INTERVAL + 60

    if req.get("phase", None) == "ChampSelect":
        debug.info("Detected champion selection.")

        current_champ = "/lol-champ-select/v1/current-champion"
        try:
            r = requests.get(URL + current_champ, headers=headers, verify=False)
        except Exception as e:
            debug.debug(e)
            debug.critical("Failed to fetch current picked champion. Aborting.")
            return MAIN_INTERVAL + 45

        if r.text and int(r.text) != 0:
            champ_id = int(r.text)
            debug.debug(champ_id)

            champion_name = get_champion_by_id(champ_id)
            if champion_name is not None:
                champion_name = _add_spaces(champion_name)

                debug.debug(champion_name)

                runes = runeforge.get_runes(champion_name)
                if not runes:
                    debug.critical(f"Could not fetch runes for {champion_name}.")
                    return
                debug.debug(runes)

                try:
                    rune_pages_url = "/lol-perks/v1/currentpage"
                    r = requests.get(URL + rune_pages_url, headers=headers, verify=False)
                except Exception as e:
                    debug.debug(e)
                    debug.error(f"Failed to fetch current runes page.")
                    return MAIN_INTERVAL + 15

                if not r.json().get('name', None).endswith(f"{champion_name} = noob champ"):
                    debug.debug(r.status_code)
                    if r.status_code == 200:
                        if r.json().get('id', None):
                            debug.info("Trying to delete current runes page.")
                            try:
                                remove_rune_url = f"/lol-perks/v1/pages/{r.json()['id']}"
                                r = requests.delete(URL + remove_rune_url, headers=headers, verify=False)

                                debug.debug(r.status_code)
                            except Exception as e:
                                debug.debug(e)
                                debug.warning(f"Failed to delete current runes page.")

                            # if r.json().get("httpStatus") == 404:
                            # print("bogactwo, intelgiencja, madrosc, dziewczyny")

                    rune_page_create = "/lol-perks/v1/pages"

                    all_runes = []

                    main_rune1 = runes[0]
                    main_rune2 = runes[1]

                    debug.debug(runes)

                    for rune in runes[2:6]:
                        rune = rune.replace(" ", "")
                        rune = rune.replace(":", "")
                        all_runes.append(runeforge.get_rune_id(main_rune1, rune))
                    for rune in runes[6:8]:
                        rune = rune.replace(" ", "")
                        rune = rune.replace(":", "")
                        all_runes.append(runeforge.get_rune_id(main_rune2, rune))

                    for rune in runes[8:10]:
                        debug.debug(rune)
                        all_runes.append(runeforge.get_shard_id(rune))

                    all_runes.extend([5001])

                    debug.debug(all_runes)

                    rune_data = {
                        "autoModifiedSelections": [
                            0
                        ],
                        "current": True,
                        "isActive": True,
                        "isDeletable": True,
                        "isEditable": True,
                        "isValid": True,
                        "lastModified": 0,
                        "name": f"{champion_name} = noob champ",
                        "order": 0,
                        "primaryStyleId": runeforge.get_primary(main_rune1),
                        "selectedPerkIds": all_runes,
                        "subStyleId": runeforge.get_primary(main_rune2)
                    }

                    debug.info("Trying to make new runes page.")
                    try:
                        r = requests.post(URL + rune_page_create, data=json.dumps(rune_data), headers=headers,
                                          verify=False)
                    except Exception as e:
                        debug.debug(e)
                        debug.error(f"Failed to make new runes page.")

                    debug.info("Made new runes page and set it as current runes page.")
                    debug.debug(0, r.json())
                    return MAIN_INTERVAL+30
                        # break
                        # data = {"id": int(r.json()["id"])}
                        # r = requests.put(URL + rune_pages_url, data=json.dumps(data), headers=headers, verify=False)
                        # print(1, r.json())
                else:
                    debug.info(f"Runes for {champion_name} are already set.")
                    return MAIN_INTERVAL + 30
        elif int(r.text) == 0:
            debug.info("Selected champion's id is 0. Continuing.")


run_ = False


def start():
    global run_
    run_ = True

    logger.info("Starting program.")
    notify.show_toast("Rune changer", "Starting program.", icon_path="ui/icon.ico", threaded=True)


def stop():
    global run_
    run_ = False

    logger.info("Stopping program.")
    notify.show_toast("Rune changer", "Stopping program.", icon_path="ui/icon.ico", threaded=True)


def main(*, client_check):
    INTERVAL = MAIN_INTERVAL
    _listener_interval = 10

    i = 0
    interval_change_in = 0

    should_wait = True

    check_client = client_check
    logger.debug(check_client)

    while True:
        if run_:
            if check_client:
                logger.info(f"Client is closed. Running process checker.")
                if misc.check_if_process_is_running("LeagueClient.exe"):
                    logger.info(f"Found League process running. Cancelling process checker.")
                    initialization()
                    check_client = False
                    should_wait = True
                    interval_change_in = 0
                    INTERVAL = MAIN_INTERVAL
                else:
                    logger.info(f"Could not found League process.")
                logger.info(f"Waiting {_listener_interval}s.")
                time.sleep(_listener_interval)
            else:
                i += 1

                if interval_change_in > 0:
                    print("more than 0")
                    print(interval_change_in)
                    interval_change_in -= 1
                elif interval_change_in == 0 and INTERVAL != MAIN_INTERVAL:
                    INTERVAL = MAIN_INTERVAL

                logger.info(f"Running phase check for {i} time.")
                new_interval = run_phase()
                if new_interval is not None and str(new_interval).isdigit():

                    logger.debug(new_interval)
                    if new_interval == 65:
                        check_client = True
                        should_wait = False

                    if new_interval is None:
                        INTERVAL = INTERVAL
                        should_wait = True
                    else:
                        INTERVAL = new_interval
                        if interval_change_in == 0:
                            interval_change_in = 5
                        # should_wait = False

                    if interval_change_in == 0:
                        INTERVAL = INTERVAL
                        should_wait = True

                if should_wait:
                    logger.info(f"Waiting {INTERVAL}s.")
                    time.sleep(INTERVAL)
        else:
            INTERVAL = MAIN_INTERVAL
            logger.info("Program is stopped.")
            logger.info(f"Waiting {INTERVAL}s.")
            time.sleep(INTERVAL)


def run():
    logger.info("Initializing.")

    data = initialization()

    try:
        main(client_check=data is not None)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Program failed. {e}")

# if __name__ == "__main__":
