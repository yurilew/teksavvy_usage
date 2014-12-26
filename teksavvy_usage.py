#!/usr/bin/env python

# ========================================
# IMPORTS
# ========================================

import os
import sys
import json
import urllib
import argparse
import requests

from ConfigParser import SafeConfigParser, NoSectionError

# ========================================
# GLOBALS AND CONSTANTS
# ========================================

ROOT_API_URL = "https://api.teksavvy.com/web/Usage/UsageSummaryRecords"

# ========================================
# FUNCTIONS
# ========================================

def _add_parameters(url, parameters):
    """ Add the supplied dictionary as parameters to the provided URL. """

    request_url = url

    for index, param in enumerate(parameters):
        if index == 0:
            ## The first query parameter is preceeded by '?'
            request_url += "?"

        elif index > 1:
            ## All subsequent parameters are separated by '&'
            request_url += "&"

        request_url += "%s=%s" % (param, urllib.quote(parameters[param]))

    return request_url    


def _get_current():
    """ Get the current month's usage. """

    request_url = _add_parameters(ROOT_API_URL, {"$filter": "IsCurrent eq true"})

    r = _make_request(request_url)

    ## Convert the JSON response into an object
    data = json.loads(r.text)

    return data["value"]


def _load_api_key():
    """ Load the Teksavvy API key. 

    The key could have been included as a "constant",
    however in this case it would have been a bad idea.
    Someone would inevitably forgot to remove their key
    before submitting and then it would become part of
    the commit history.

    The file where the API key is stored, is located in
    the user's home directory so that it can be easily
    accessed when this script is run as a cron job.
    See the --notify-current option.
    """

    your_api_key_goes_here = "YOUR-TEKSAVVY-API-KEY-GOES-HERE"

    api_keys_filepath = os.path.join(os.path.expanduser("~"), ".api_keys.ini")
    if not os.path.exists(api_keys_filepath):
        with open(api_keys_filepath, "w") as handle:
            print >> handle, "[TEKSAVVY]"
            print >> handle, "API_KEY = %s" % your_api_key_goes_here

    parser = SafeConfigParser()
    parser.read(api_keys_filepath)

    api_key = None

    try:
        api_key = parser.get("TEKSAVVY", "API_KEY")

    except NoSectionError as e:
        with open(api_keys_filepath, "a") as handle:
            print >> handle, ""
            print >> handle, "[TEKSAVVY]"
            print >> handle, "API_KEY = %s" % your_api_key_goes_here

    if api_key is None or api_key == your_api_key_goes_here:
        print "Please add your Teksavvy API key to the file %s" % api_keys_filepath
        return None

    return api_key


def _notify(summary = "Teksavvy Usage", message = None):
    """ Emit a desktop notification. """

    os.system("notify-send -u normal '%s' '%s' &> /dev/null" % (summary, message))


def _make_request(url):
    """ Make a request to the Teksavvy API. """

    r = requests.get(url, headers={"TekSavvy-APIKey": APIKEY})

    if r.status_code != 200:
        print "Requests returned code: %s" % r.status_code
        print r.text
        sys.exit(0)

    return r


# ========================================
# MAIN
# ========================================

def notify_current():
    """ Display a desktop notification for the current month's usage. """

    values = _get_current()

    ## We only care about on peak downloads, since
    ## off peak downloads and all uploads are free
    usage = values[0]["OnPeakDownload"]

    _notify(message = "You have used %s GB so far this month." % usage)


def show_all():
    """ Show the entire usage history. """

    r = _make_request(ROOT_API_URL)

    ## Convert the JSON response into an object
    data = json.loads(r.text)

    ## Print the entire usage history
    values = data["value"]
    for dictionary in values:
        print "----------------------------------------"
        for key in dictionary.keys():
            print "%18s: %s" % (key, dictionary[key])

    return 0


def show_current():
    """ Show the current month's usage history. """

    values = _get_current()

    ## Print the current month's data
    for month in values:
        print "----------------------------------------"
        for key in month.keys():
            print "%18s: %s" % (key, month[key])

    return 0


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description = "Get your Teksavvy usage.")

    PARSER.add_argument("--all",
                        action="store_true",
                        dest="all",
                        default=True,
                        help="Show the entire usage history.")

    PARSER.add_argument("--current",
                        action="store_true",
                        dest="current",
                        help="Show the current month's usage.")

    PARSER.add_argument("--notify-current",
                        action="store_true",
                        dest="notify_current",
                        help="Display a desktop notification with the current month's usage.")

    ARGS = PARSER.parse_args()

    global APIKEY
    APIKEY = _load_api_key()

    if APIKEY is None:
        sys.exit(1)
    

    if ARGS.current:
        sys.exit(show_current())

    elif ARGS.notify_current:
        sys.exit(notify_current())

    elif ARGS.all:
        sys.exit(show_all())
