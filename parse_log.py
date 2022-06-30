import argparse
import json
import os.path
import re

parser = argparse.ArgumentParser()
parser.add_argument('--path_to_file', dest='path_to_file', help='Path to log_file')
args = parser.parse_args()

if os.path.isfile(args.path_to_file):
    result_json = {
        "file_name": args.path_to_file,
        "total_requests_number": 0,
        "3_ip_with_greatest_requests_number": {},
        "3_slowest_requests": [],
        "requests_by_method": {
            "GET": 0,
            "POST": 0,
            "PUT": 0,
            "DELETE": 0,
            "PATCH": 0,
            "HEAD": 0,
            "CONNECT": 0,
            "OPTIONS": 0,
            "TRACE": 0
        }
    }

    requests_by_all_ips = {}

    with open(args.path_to_file) as file:
        idx = 0

        for line in file:
            idx +=1

            ip_match = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            date_match = re.search(
                "\d\d/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/\d\d\d\d:\d\d:\d\d:\d\d \+\d\d\d\d", line)
            method_match = re.search('] \"(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)', line)
            url_match = re.search('"(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH) (\S+) +HTTP', line)
            timing_str = line.split(" ")[-1]

            if ip_match and date_match and method_match and url_match:
                ip = ip_match.group()
                date = date_match.group()
                method = method_match.group(1)
                url = url_match.group(2)
            else:
                continue

            try:
                timing = int(timing_str)
            except ValueError:
                continue

            # Number of method
            result_json["requests_by_method"][method.upper()] += 1

            # Top 3 slowest requests
            if len(result_json["3_slowest_requests"]) < 3:
                result_json["3_slowest_requests"].append([ip, date, method, url, timing])
            else:
                minimal = min(result_json["3_slowest_requests"][0][-1], result_json["3_slowest_requests"][1][-1],
                              result_json["3_slowest_requests"][2][-1])

                if timing > minimal:
                    if result_json["3_slowest_requests"][0][-1] == minimal:
                        result_json["3_slowest_requests"].remove(result_json["3_slowest_requests"][0])
                    elif result_json["3_slowest_requests"][1][-1] == minimal:
                        result_json["3_slowest_requests"].remove(result_json["3_slowest_requests"][1])
                    elif result_json["3_slowest_requests"][2][-1] == minimal:
                        result_json["3_slowest_requests"].remove(result_json["3_slowest_requests"][2])

                    result_json["3_slowest_requests"].append([ip, date, method, url, timing])

            # top 3 most IPs with the greatest requests number
            if ip in requests_by_all_ips:
                requests_by_all_ips[ip] += 1
            else:
                requests_by_all_ips[ip] = 1

        sorted_keys = sorted(requests_by_all_ips, key=requests_by_all_ips.get, reverse=True)
        for i in range(3):
            result_json["3_ip_with_greatest_requests_number"][sorted_keys[i]] = requests_by_all_ips[sorted_keys[i]]

        # All requests number
        result_json["total_requests_number"] = idx

    print(json.dumps(result_json, indent=4))

    with open(
            f"result.json",
            "w") as file:
        file.write(json.dumps(result_json, indent=4))