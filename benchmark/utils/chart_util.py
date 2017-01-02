import mongo_util
import stats_util


def construct_char(chart_id):
    servers = mongo_util.get_all_servers()
    chart = mongo_util.get_chart(chart_id)
    stats = stats_util.get_all_statistics_avg()
    pairs = []
    for server_id in chart["servers"]:
        name = get_name_of_server_in_chart(servers, server_id, chart)
        value = get_value_of_server(servers, server_id, chart, stats)
        pair = [name, value]
        pairs.append(pair)
    chart["pairs"] = pairs
    return chart


def get_name_of_server_in_chart(servers, server_id, chart):
    name_keys = chart["x_axis_names"]
    name_key_values = []
    for server in servers:
        if server["id"] == server_id:
            for name_key in name_keys:
                if name_key == "core":
                    value = unicode(server[name_key]) + "C"
                elif name_key == "memory":
                    value = unicode(server[name_key]) + "G"
                else:
                    value = unicode(server[name_key])

                name_key_values.append(value)
    return '-'.join(name_key_values)


def get_value_of_server(servers, server_id, chart, stats):
    chart_key = chart["key"]

    server_ip = get_server_ip_by_id(server_id, servers)

    # get stat data
    for stat in stats:
        if stat["ip"] == server_ip:
            server_stat = stat
            break

    for server in servers:
        if server["id"] == server_id:
            keys = chart_key.split('/')
            for key in keys:
                server_stat = server_stat.get(key)
            return server_stat


def get_server_ip_by_id(server_id, servers):
    for server in servers:
        if server["id"] == server_id:
            return server["ip"]
