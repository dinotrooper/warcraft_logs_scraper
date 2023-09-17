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

def get_encounter_name(wcl: ApiConnector, encounter_id) -> str:
    log_dir = "./log/"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    last_response_filename = "last_response.txt"
    response_json = wcl.generic_request(get_encounter_query(encounter_id))
    if not is_response_good(response_json):
        logging.error(f"response_json is bad: {response_json}")
        return
    with open(os.path.join(log_dir, last_response_filename), "w") as last_respone_file:
        json.dump(response_json, last_respone_file)
    try:
        encounter_name = response_json["data"]["worldData"]["encounter"]["name"]
    except:
        logging.error("encounter name not in response json")
        logging.debug("response_json = %s", response_json)
        return
    return encounter_name
    

def get_encounter_query(encounter_id) -> str:
    encounter_id = encounter_id.strip()
    return f"""
    query {{
        worldData {{
            encounter(id: {encounter_id}) {{
                name
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
    with open(output_fp, "w") as output_file:
        for name in get_names():
            # for encounter_id in get_encounter_ids():
            encounter_id = get_encounter_ids()[0]
            encounter_name = get_encounter_name(wcl, encounter_id)
            median_perf = get_median_perf(wcl, name, encounter_id)
            output_file.write(f"{name} - median perf: {median_perf} on {encounter_name}\n")

def get_median_perf(wcl: ApiConnector, name: str, encounter_id: str):
    response_json = wcl.generic_request(get_best_perf_avg_query(name, encounter_id))
    if not is_response_good(response_json):
        logging.error(f"response_json is bad: {response_json}")
        return
    try:
        median_perf = response_json["data"]["characterData"]["character"]["encounterRankings"]["medianPerformance"]
    except:
        logging.error("response_json is missing median_perf")
        logging.debug("response_json = %s", response_json)
        return None
    median_perf = round(float(median_perf), 2)
    return median_perf

def is_response_good(response):
    return not any([
        response is None,
        "errors" in response,
    ])

if __name__ == "__main__":
    main()