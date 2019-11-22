import argparse
import re
import urllib.request
import sys
import os
from urllib.parse import urlparse
from datetime import datetime, timezone


# making sure that the URL is valid
def validate_url(location):
    try:
        result = urlparse(location)
        if all([result.scheme, result.netloc, result.path]):
            return True

    # should be specific to specific error
    except Exception as e:
        # best to log instead of printing to STDOUT
        print(e)
        return False


def nginx_pattern():
    pattern = (r''
               '(?P<ipaddress>[^\s]+)' # remote address (changed for IPv4 and IPv6)
               '\s-\s-\s' # remote user
               '\[(?P<date_time>.+)\]\s' # time local
               '(?P<request>".*?")\s' # request
               '(?P<status>(\d+))\s' # status
               '(?P<bytes_sent>(\d+))\s' #bytes sent
               '(?P<http_referer>".*?")\s' # http referer 
               '(?P<http_user_agent>".*?")' # http user agent

    )
    return pattern


def get_content(url):
    try:
        request = urllib.request.Request(url)
        return urllib.request.urlopen(request)
    except Exception as e:
        # TODO: Granular exception and pass errors to log instead of STDOUT
        print(e)
        sys.exit()


def parse_content(response):
    # setting time to now and epoch for comparison
    start_time = datetime.now(timezone.utc)
    end_time = datetime.strptime('1/Jan/1970:00:00:00 +0000', '%d/%b/%Y:%H:%M:%S %z')
    code = {}
    total = 0
    prog = re.compile(nginx_pattern())
    for line in response:
        try:
            parsed = prog.search(line.decode("utf-8").rstrip())
            # logs may be out of order so time needs to be compared
            temp = parsed.groupdict()
            converted_time = datetime.strptime(temp['date_time'], '%d/%b/%Y:%H:%M:%S %z')
            if converted_time < start_time:
                start_time = converted_time
            if converted_time > end_time:
                end_time = converted_time
            if temp['status'] in code:
                code[temp['status']] += 1
            else:
                code[temp['status']] = 1
            total += 1
        except Exception as e:
            # TODO: Granular exception and pass errors to log instead of STDOUT
            print(e)
            pass

    response.close()
    output_result(start_time, end_time, code, total)


def output_result(start_time, end_time, code, total):
    code_output = []
    err = []
    ok = ""
    for k, v in sorted(code.items()):
        code_output.append("{} {} responses,".format(v, k))
        if str(k).startswith('4') or str(k).startswith('5'):
            err.append("{:.2%} {} errors, ".format(v/total, k))
        if str(k).startswith('2'):
            ok = "{:.2%}".format(v/total)

    http_code = ' and '.join(code_output)
    error = ''.join(err)
    start = start_time.strftime('%d/%b/%Y:%H:%M:%S %z')
    end = end_time.strftime('%d/%b/%Y:%H:%M:%S %z')

    output = "The site has returned a total of {} out of total {} requests between time {} and time {}. " \
             "That is a {}and {} of 200 responses.".format(http_code, total, start, end, error, ok)
    print(output)


if __name__ == '__main__':
    try:
        url = os.environ['URL']
        data = get_content(url)
        parse_content(data)
    except Exception as e:
        # TODO: Granular exception and pass errors to log instead of STDOUT
        print(e)


