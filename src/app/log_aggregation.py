import argparse
from urllib.parse import urlparse

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--url', dest='url',
                        help='The URL to pull the logs from')

    args = parser.parse_args()
    print(validate_url(args.url))

