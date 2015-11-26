################################################################################
import os
import sys

if __name__ == "__main__":
    # prevent python from generating compiled byte code (.pyc).
    sys.dont_write_bytecode = True
    # append parent directory ("pyzzle") to python path.
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import codecs
import gzip
import json
import StringIO
import datetime

from tools.http import HttpClient
from tools.log import Log
from tools.parsejson import parse_json

################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################
# global constants
k_path_log = "./log"
k_last_refresh = "last_refresh"
k_interval = 1800

################################################################################
# constants used in api_call()
k_content_type = "content-type"
k_json_gz = "json-gz"

################################################################################
# global variables
g_config = None
g_config_file = None
g_httpclient = None


def save_to_file(thepath, thefile, content):
    if not content:
        content = {}
    data = Log.beautify_json(content) if type(content) is not str else content

    if not os.path.exists(thepath):
        os.makedirs(thepath)
    try:
        filepath = "%s/%s" % (thepath, thefile)
        with codecs.open(filepath, "w", "utf-8-sig") as f:
            f.write(unicode(data, "utf-8"))
            f.write("\r\n")
    except UnicodeDecodeError as e:
        print "UnicodeDecodeError: %s" % e
    except IOError as e:
        print "IOError: %s" % e
    pass


def decompress(gz):
    compressedfile = StringIO.StringIO(gz)
    decompressedfile = gzip.GzipFile(fileobj=compressedfile)
    return decompressedfile.read()


def api_call(method, url, datadict):
    if url is None or method is None:
        return

    global g_httpclient
    if method == "post":
        resp = g_httpclient.post(url, datadict)
    else:
        resp = g_httpclient.get(url, datadict)
    httpcode = resp.getcode()
    response = resp.read()
    headers = resp.info()

    if k_content_type in headers and headers[k_content_type].find(k_json_gz) != -1:
        response = decompress(response)
    return httpcode, response


# check_refresh_interval() checks the the elapsed from last refresh, it returns
# True if the elapsed time exceeds the default interval or the one defined in
# config file, or False otherwise.
def check_refresh_interval():
    global g_config
    diff_seconds = -1
    now = datetime.datetime.now()
    # force to refresh between the time 00:00:00 to 00:00:05
    if now.hour == 0 and now.minute < 5:
        return True
    if k_last_refresh in g_config:
        diff = now - datetime.datetime.strptime(g_config[k_last_refresh], "%Y%m%d%H%M%S")
        diff_seconds = diff.seconds
    interval = g_config["interval"] if "interval" in g_config else k_interval
    return diff_seconds >= interval if diff_seconds != -1 else True


def refresh_log(data=None):
    save_to_file(k_path_log, datetime.datetime.now().strftime("%Y%m%d%H%M%S"), data)


# on_refresh_character() is a callback function called from load_json() if
#   there is "handler" defined in config file.
def on_refresh_character(httpcode, response):
    global g_config
    if httpcode == 200:
        d_user = json.loads(response)
        if refresh_log in g_config and g_config["refresh_log"] == "yes":
            refresh_log(d_user)
        fresh = d_user["fresh_character"] if "fresh_character" in d_user else 0
        if fresh is 1:
            g_config[k_last_refresh] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            save_to_file(".", g_config_file, g_config)
    pass


# load_json() loads the config from a json file and send the request per the
# definitions of the config file.
# an example of config file:
#      {
#      "method" : "post",
#      "url": "http://url.to/api/foobar",
#      "data": {"name": "value"},
#      "handler": "on_refresh_character",
#      "refresh_log": "yes",
#      "__end__": ""
#      }
def load_json():
    if len(sys.argv) < 3:
        show_usage()
        return
    global g_config_file, g_config
    g_config_file = sys.argv[2]
    g_config = parse_json(g_config_file)
    if not check_refresh_interval():
        return
    datadict = g_config["data"] if "data" in g_config else None
    method = g_config["method"]
    url = g_config["url"]
    httpcode, response = api_call(method, url, datadict)
    print "%d %s %s" % (httpcode, url, response)
    if "handler" in g_config:
        handler = "%s(%s,%s)" % (g_config["handler"], "httpcode", "response")
        eval(handler)
    pass


def initialize():
    global g_httpclient
    g_httpclient = HttpClient()
    pass


def show_usage():
    appname = os.path.basename(__file__)
    print "usage:"
    print "  python " + appname + " load" + " { config_file }"
    print ""
    pass


def main():
    if len(sys.argv) < 2:
        show_usage()
        return
    initialize()
    mode = sys.argv[1]
    if mode == "help":
        show_usage()
    elif mode == "load":
        load_json()
    else:
        show_usage()
    pass


################################################################################

if __name__ == "__main__":
    main()
    pass
