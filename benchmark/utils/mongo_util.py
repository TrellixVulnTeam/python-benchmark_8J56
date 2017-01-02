from pymongo import MongoClient
from benchmark import settings

client = MongoClient(settings.mongodb_host, settings.mongodb_port)
db = client[settings.mongodb_database]


# results
def insert_test_result(test_result):
    ip = test_result["ip"]
    time_str = test_result["time_str"]
    collection = db[settings.mongodb_collection_results]
    collection.update({"ip": ip, "time_str": time_str}, test_result,
                      upsert=True)


def find_one_result(ip, time_str):
    collection = db[settings.mongodb_collection_results]
    result = collection.find_one({"ip": ip, "time_str": time_str})
    return result


def find_test_results(ip):
    collection = db[settings.mongodb_collection_results]
    results = collection.find({"ip": ip})
    return results


def find_test_results_by_server_id(server_id):
    server = get_server("id", server_id)
    ip = server["ip"]
    return find_test_results(ip)


def result_existed(ip, time_str):
    result = find_one_result(ip, time_str)
    return True if result else False


def truncate_test_results():
    collection = db[settings.mongodb_collection_results]
    collection.delete_many({})


# servers
def insert_server(server):
    ip = server["ip"]
    collection = db[settings.mongodb_collection_servers]
    collection.update({"ip": ip}, server, upsert=True)


def insert_many_server(servers):
    for server in servers:
        insert_server(server)


def get_server(key, value):
    collection = db[settings.mongodb_collection_servers]
    results = collection.find({key: value})
    return results


def get_all_servers():
    collection = db[settings.mongodb_collection_servers]
    servers = collection.find({})
    return list(servers)


def truncate_servers():
    collection = db[settings.mongodb_collection_servers]
    collection.delete_many({})


# charts
def insert_chart(chart):
    id = chart["id"]
    collection = db[settings.mongodb_collection_charts]
    collection.update({"id": id}, chart, upsert=True)


def get_chart(chart_id):
    collection = db[settings.mongodb_collection_charts]
    chart = collection.find_one({"id": chart_id})
    return chart


def insert_many_charts(charts):
    for chart in charts:
        insert_chart(chart)


def truncate_charts():
    collection = db[settings.mongodb_collection_charts]
    collection.delete_many({})
