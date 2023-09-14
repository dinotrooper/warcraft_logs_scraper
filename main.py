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

def get_best_perf_avg_query(name) -> str:
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
                    encounterID: 629
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
    with open(output_fp, "w+") as output_file:
        for name in get_names():
            response_json = wcl.generic_request(get_best_perf_avg_query(name))
            if response_json is None:
                logging.error("response_json is None")
                continue
            if "errors" in response_json:
                logging.error(response_json["errors"])
                continue
            try:
                median_perf = response_json["data"]["characterData"]["character"]["encounterRankings"]["medianPerformance"]
            except:
                logging.error(f"median_pref is missing data: {median_perf}")
            output_file.write(f"{name} - median perf: {median_perf}\n")

if __name__ == "__main__":
    main()