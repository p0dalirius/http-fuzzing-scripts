#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : fuzz_url_lent.py
# Author             : Podalirius (@podalirius_)
# Date created       : 14 May 2022

import requests
import argparse
from enum import Enum
import matplotlib.pyplot as plt


class RequestStatus(Enum):
    OK = 0
    HTTP_200 = 200
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_414 = 414
    HTTP_500 = 500
    HTTP_501 = 501
    HTTP_502 = 502
    HTTP_503 = 503
    ReadTimeout = 1001
    ConnectTimeout = 1002
    ConnectionError = 1003


def test(baseurl, lenght, timeout=1):
    try:
        length = lenght - (len(baseurl) + 2)
        testurl = baseurl + "/" + "."*length + "/"
        r = requests.get(testurl, timeout=timeout)
    except requests.exceptions.ReadTimeout as e:
        return RequestStatus.ReadTimeout
    except requests.exceptions.ConnectTimeout as e:
        return RequestStatus.ConnectTimeout
    except requests.exceptions.ConnectionError as e:
        return RequestStatus.ConnectionError
    return RequestStatus.OK


def dichotomic_search(url, timeout=1, max_urllen_test=150000):
    urllen, step = 1000, 1000
    normal_response = test(url, len(url), timeout=timeout)
    last_result = normal_response
    k, x, y = 0, [], []
    if last_result == normal_response:
        while step >= 1 and 0 < urllen <= max_urllen_test:
            k += 1
            x.append(k)
            y.append(urllen)
            result = test(url, urllen, timeout=timeout)
            print("   [>] Testing URL length %d, (%s => %s)" % (urllen, result.name, last_result.name))
            if last_result == RequestStatus.OK:
                if result == RequestStatus.OK:
                    urllen = urllen + step
                else:
                    # Too long
                    step = step//2
                    urllen = urllen - step
            else:
                if result == normal_response:
                    step = step//2
                    urllen = urllen + step
                else:
                    # Too long
                    urllen = urllen - step
            last_result = result
        if urllen <= 0 or urllen >= max_urllen_test:
            print("[!] Could not determine maximum URL length. (Maybe we can't connect to this URL?)")
        else:
            plt.plot(x, [urllen for k in x], color="red", label='Maximum URL length (%d)' % urllen)
            plt.plot(x, y, color="blue", label='Dichotomic search')
            plt.scatter(x, y, color="blue")
            plt.legend()
            plt.grid()
            plt.show()
            print("[+] Found maximum URL length %d" % urllen)
    else:
        print("[!] Could connect to this URL. (%s)" % last_result)


def parse_args():
    parser = argparse.ArgumentParser(description="description")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Verbose mode")
    parser.add_argument("-u", "--url", dest="url", action="store", type=str, required=True, help="URL to connect to.")
    parser.add_argument("-k", "--insecure", dest="insecure_tls", action="store_true", default=False, help="Allow insecure server connections when using SSL (default: False)")
    parser.add_argument("-t", "--timeout", dest="timeout", action="store", type=int, default=1, required=False, help="Timeout of requests in seconds. (default: 1)")
    return parser.parse_args()


if __name__ == '__main__':
    options = parse_args()

    if not options.url.startswith("http://") and not options.url.startswith("https://"):
        options.url = "https://" + options.url
    options.url = options.url.rstrip('/')

    if options.insecure_tls:
        # Disable warings of insecure connection for invalid certificates
        requests.packages.urllib3.disable_warnings()
        # Allow use of deprecated and weak cipher methods
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            pass

    print("[+] Dichotomic search of maximum URL length ...")
    dichotomic_search(options.url, options.timeout)
