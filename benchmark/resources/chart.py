import json
from flask import jsonify
from flask_restful import Resource

import bson.json_util

import utils.chart_util as chart_util
import mylog

LOG = mylog.setup_custom_logger(__name__)


class Chart(Resource):
    @staticmethod
    def get(chart_id):
        try:
            data = chart_util.construct_char(int(chart_id))
            data = json.loads(bson.json_util.dumps(data))
            ret = {"code": 0, "message": "", "data": data}
            return jsonify(ret)
        except Exception, exception:
            LOG.exception(exception)
            # traceback.format_exc()
            return jsonify({"code": 1, "message": str(exception)})
