# log_processing

This is a small application that processes logs that takes in the URL as an environment variable.

To build: 
```shell script
docker build -t log_processing .
``` 

To run: 
```shell script
docker run --env URL='https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_logs/nginx_logs' log_processing
```