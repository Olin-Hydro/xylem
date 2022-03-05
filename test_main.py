from main import create_query, send_request, parse_line, parse_res, SYS_PARAMS
import json


def test_create_query():
    data = {
        "data_type": "system",
        "req_type": "get",
        "name": "phSenseInterval",
        "data": "1",
    }
    query, variables = create_query(data)
    assert query == "query sysQuery($id: ID) {sysParams(id:$id){phSenseInterval}}"
    assert variables == {"id": "1"}


def test_send_request_sys():
    query = "query sysQuery($id: ID) {sysParams(id:$id){phSenseInterval}}"
    variables = {"id": "1"}
    res = send_request(query, variables)
    data = json.loads(res.text)
    print(data)
    assert isinstance(data["data"][SYS_PARAMS][0]["phSenseInterval"], int)


def test_main_get_sys():
    line = "system:get:phSenseInterval:1"
    data = parse_line(line)
    query, variables = create_query(data)
    res = send_request(query, variables)
    return_data = parse_res(res, data)
    assert isinstance(return_data, int)


def test_main_post_ph():
    line = "sensor:post:ph:6.8"
    data = parse_line(line)
    query, variables = create_query(data)
    res = send_request(query, variables)
    return_data = parse_res(res, data)
    assert return_data == 200


def test_main_post_task():
    line = "task:post:ec:0"
    data = parse_line(line)
    query, variables = create_query(data)
    res = send_request(query, variables)
    return_data = parse_res(res, data)
    assert return_data == 200
