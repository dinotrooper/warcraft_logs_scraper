from typing import List
import logging
import json
import os
from api_connector import ApiConnector

def get_names() -> List[str]:
    name_fp = "names.txt"
    names = []
    with open(name_fp, "r") as name_file:
        tmp_names = name_file.readlines()
    for name in tmp_names:
        names.append(name.strip())
    return names

def get_encounter_ids() -> List[str]:
    filepath = "encounter_ids.txt"
    id_list = []
    with open(filepath, "r") as encounter_file:
        tmp_ids = encounter_file.readlines()
    for tmp_id in tmp_ids:
        id_list.append(tmp_id.strip())
    return id_list

def get_encounter_name(encounter_id) -> str:
    pass


def get_encounter_query(encounter_id) -> str:
    name = name.strip()
    return f"""
    query {{
        characterData {{
            character(
                name: "{name}"
                serverSlug: "Faerlina"
                serverRegion: "US"
            ) {{
                id
                name
                encounterRankings(
                    encounterID: {encounter_id}
                )
            }}
        }}
    }}
    """


def get_best_perf_avg_query(name, encounter_id) -> str:
    name = name.strip()
    return f"""
    query {{
        characterData {{
            character(
                name: "{name}"
                serverSlug: "Faerlina"
                serverRegion: "US"
            ) {{
                id
                name
                encounterRankings(
                    encounterID: {encounter_id}
                )
            }}
        }}
    }}
    """

def main():
    log_dir = "./log/"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file = "main.log"
    full_log_path = os.path.join(log_dir, log_file)
    output_fp = os.path.join(log_dir, "response.txt")
    logging.basicConfig(filename=full_log_path, encoding='utf-8', level=logging.DEBUG)
    keys = {
        "discord_token": None,
        "client_id": None,
        "client_secret": None
    }
    with open(".keyfile") as f:
        keys = json.load(f)
    wcl = ApiConnector(keys["client_id"], keys["client_secret"], logging)
    for name in get_names():
        for encounter_id in get_encounter_ids():
            with open(output_fp, "w") as output_file:
                response = get_median_perf(wcl, name, encounter_id)
                logging.debug("response = %s", response)
                if response == None:
                    continue
                encounter_name, median_perf = response
                output_file.write(f"{name} - median perf: {median_perf} on {encounter_name}\n")

def get_median_perf(wcl: ApiConnector, name: str, encounter_id: str):
    response_json = wcl.generic_request(get_best_perf_avg_query(name, encounter_id))
    if not is_response_good(response_json):
        logging.error(f"response_json is bad: {response_json}")
        return
    try:
        encounter_name = response_json["data"]["characterData"]["character"]["encounterRankings"]["name"]
    except:
        encounter_name = None
        logging.error("response_json is missing encounter_name")
        logging.debug("response_json = %s", response_json)
    try:
        median_perf = response_json["data"]["characterData"]["character"]["encounterRankings"]["medianPerformance"]
    except:
        logging.error("response_json is missing median_perf")
        logging.debug("response_json = %s", response_json)
        median_perf = None
    return encounter_name, median_perf

def is_response_good(response):
    return not any([
        response is None,
        "errors" in response,
    ])

if __name__ == "__main__":
    main()