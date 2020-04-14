import random

import requests

from bs4 import BeautifulSoup

r = requests.get("https://runeforge.gg/all-loadouts-data.json")
runes_req = r.json()

r = requests.get("https://ddragon.leagueoflegends.com/cdn/10.7.1/data/en_US/runesReforged.json")
rune_id_req = r.json()

r = requests.get("https://ddragon.leagueoflegends.com/cdn/10.7.1/data/en_US/runesReforged.json")
primary_req = r.json()


def get_runes(champion_name):
    runes = []
    url = None

    for d in runes_req:
        if d.get("loadout_champion_name").lower() == champion_name.lower():
            url = d.get("loadout_url", None)
    if url:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        a = soup.find_all("a")
        # p = soup.find_all("p")
        h2 = soup.find_all("h2")

        for rune in h2:
            if rune.get('class', ['not rune-name'])[0] == "rune-name":
                if rune.text is not None: runes.append(rune.text)

        for rune in a:
            if rune.get('class', ['not rune-name'])[0] == "rune-name":
                if rune.text is not None: runes.append(rune.text)

        ps = soup.find_all("div", {"class": "rune-path--rune_description"})
        sr = ["+9% Attack Speed", "+5 AD or 9 AP", "+6 Armor", "+1-10% CDR", "+8 Magic Resist"]
        for elem in ps:
            t = elem.find('p').text
            if t in sr:
                runes.append(t)

        if len(runes) == 11:
            runes.remove(runes[-1])

        elif len(runes) < 10:
            runes.append(random.choice(["+5 AD or 9 AP", "+6 Armor", "+8 Magic Resist"]))

        # for rune in p:
        #     if rune.get('class', ['not rune-name'])[0] == "rune-name":
        #         if rune.text is not None: runes.append(rune.text)
    return runes


def get_shard_id(shard_desc):
    shard_map = {
        "+6 Armor": 5002,
        "+8 Magic Resist": 5003,
        "+5 AD or 9 AP": 5008,
        "+15-90 Health": 5001,
        "+1-10% CDR": 5007,
        "+9% Attack Speed": 5005,
    }
    return shard_map.get(shard_desc)


    # #r = requests.get("http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json")
    # #req = r.json()
    #
    # # for rune in req:
    #     # print(rune)
    #     # if rune.get('tooltip', None) == shard_desc:
    #         # print(rune)
    #         return rune['id']


def get_rune_id(main_rune, rune_name, is_key=True):
    if is_key:
        key = "key"
    else:
        key = "id"

    rune_name = rune_name.replace(" ", "")

    for d in rune_id_req:
        if d.get(key, None) == main_rune:
            for slot in d["slots"]:
                for rune in slot["runes"]:
                    if rune.get("key", None).lower() == rune_name.lower():
                        return rune['id']


def get_primary(main_rune):
    main_rune = main_rune.replace(" ", "")

    for d in primary_req:
        if d.get("key", None) == main_rune:
            return d.get('id', None)


if __name__ == "__main__":
    print(get_runes("Amumu"))
    print(get_runes("Akali"))
    print(get_runes("Lee Sin"))
    print(get_runes("Aatrox"))
    print(get_runes("Kha'Zix"))
    print(get_shard_id(get_runes("Garen")[-1]))
