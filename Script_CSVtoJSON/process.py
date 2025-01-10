import sys
import os
import json
import random

out_dir = "out"
os.makedirs(out_dir, exist_ok=True)

geojson_dir = "municipal-brazilian-geodata/data"
geojson_combined = None


def combine_geojson():
    for filename in os.listdir(geojson_dir):
        if filename == "Brasil.json":
            continue
        filepath = os.path.join(geojson_dir, filename)
        with open(filepath) as file:
            feature_col = json.load(file)
            if not geojson_combined:
                geojson_combined = {
                    "type": feature_col["type"],
                    "crs": feature_col["crs"],
                    "features": [],
                }
            geojson_combined["features"].extend(feature_col["features"])

    with open(os.path.join(out_dir, "Brazil_ADM2.geojson"), "w") as file:
        json.dump(geojson_combined, file)


def parse_line(l):
    return [s.strip('"') for s in l.strip('"\n').split(",")]


def make_cluster(filename, cluster_id, cluster_name, key_attribute):
    with open(filename, encoding="utf-8-sig") as file:
        nodes = []
        geocodes_seen = set()

        keys = parse_line(next(file))
        for line in file:
            values = parse_line(line)
            raw_attributes = dict(zip(keys, values))
            geocode = raw_attributes["geocode"]
            if geocode not in geocodes_seen:
                node = {
                    "id": len(nodes),
                    "nodeLabel": raw_attributes["municipality"],
                    "nodeDescription": "",
                    "nodeAttributes": {"attRaw": raw_attributes},
                    "connectors": ["geo"],
                    "pajekIndex": 0,
                    "vNode": {
                        "posX": -999,
                        "posY": -999,
                        "posZ": 0,
                        "color": "#ffffff",
                    },
                }
                nodes.append(node)
                geocodes_seen.add(geocode)

        return {
            "clusterID": cluster_id,
            "clusterType": "geo",
            "clusterLabel": cluster_name,
            "clusterDescription": "",
            "keyAttribute": key_attribute,
            "nodes": nodes,
        }


dataset = {
    "nodes": [
        make_cluster(
            "TRAJETORIAS_DATASET_Environmental_dimension_indicators.csv",
            "0",
            "Environmental",
            "defor",
        ),
        make_cluster(
            "TRAJETORIAS_DATASET_Socio-Economic_dimension-indicators.csv",
            "1",
            "Socio-Economic",
            "ipm",
        ),
    ],
    "edges": [],
}

for i in range(1000):
    source_cluster = random.choice(range(2))
    source_index = random.choice(range(300))
    target_cluster = random.choice(range(2))
    target_index = random.choice(range(300))
    dataset["edges"].append(
        {
            "source": {
                "cluster": str(source_cluster),
                "index": source_index,
                "pajekIndex": 0,
            },
            "target": {
                "cluster": str(target_cluster),
                "index": target_index,
                "pajekIndex": 0,
            },
            "kind": "geo",
            "weight": 1,
        }
    )

with open(os.path.join(out_dir, "3_network.json"), "w") as file:
    json.dump(dataset, file)
