import serial
import os
import requests
import json


SERIAL_PORT = os.getenv("SERIAL_PORT", "Missing SERIAL_PORT environment variable")
BAUDRATE = os.getenv("BAUDRATE", "Missing BAUDRATE environment variable")
API_URL = os.getenv("API_URL", "Missing API_URL environment variable")
SYS_PARAMS = "sysParams"


def run():
    s = serial.Serial(find_arduino(SERIAL_PORT), BAUDRATE, timeout=1)
    print("Starting loop")
    while True:
        if s.in_waiting > 0:
            line = read_data(s)
            data = parse_line(line)
            if not data:
                print(f"Failed parsing data")
                continue
            query, variables = create_query(data)
            res = send_request(query, variables)
            if res.status_code != 200:
                print(f"Error sending api request: {res}")
            return_data = parse_res(res, data)
            print(f"Relaying Message: \n {return_data} \n from: \n{res.text}")
            s.write(bytes(res.text, "utf-8"))


def parse_res(res, data):
    res_data = json.loads(res.text)["data"]
    if data["req_type"] == "get":
        return res_data[SYS_PARAMS][0][data["name"]]
    return res.status_code


def read_data(s):
    print("Reading")
    line = s.read_until().decode("utf-8").rstrip("\n")
    print(line)
    return line


def parse_line(line):
    data_list = line.split(":")
    if len(data_list) != 4:
        return None
    data_list = [item.strip() for item in data_list]
    return {
        "data_type": data_list[0],
        "req_type": data_list[1],
        "name": data_list[2],
        "data": data_list[3],
    }


def create_query(data: dict):
    if data["data_type"] == "sensor":
        query = """mutation senseQuery($dtype: String, $data: Float){createSensorLog(input:{type:$dtype, data: $data}){id}}"""
        variables = {"dtype": data["name"], "data": float(data["data"])}
    elif data["data_type"] == "task":
        query = """mutation taskQuery($dtype: String, $data: String){createTaskLog(input:{type:$dtype, data: $data}){id}}"""
        variables = {"dtype": data["name"], "data": data["data"]}
    elif data["data_type"] == "system":
        query = "query sysQuery($id: ID) {sysParams(id:$id){" + data["name"] + "}}"
        variables = {"id": data["data"]}
    else:
        return None
    return query, variables


def send_request(query, variables):
    return requests.post(
        API_URL,
        json={"query": query, "variables": variables},
    )


def find_arduino(port=None):
    if port is None:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.manufacturer is not None and "Arduino" in p.manufacturer:
                port = p.device
    return port
