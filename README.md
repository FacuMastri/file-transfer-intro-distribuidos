# FileTransfer-grupo7

## Test the file upload

First start the server

     python3 src/start_server.py -v -H 127.0.0.1 -p 12000

Open a new terminal and upload a file

     python3 src/upload.py -v -H 127.0.0.1 -p 12000 --src src/donald.jpeg --name donald.jpeg


Then check new file in `server/files/donald.jpeg`

## Test with packet loss

`device` parameter should be the name of the network interface (e.g. `eth0`) and it can be found with `wireshark`

    comcast -device=lo --packet-loss=10% -target-addr=127.0.0.1

## Dependencies

Creating virtual environment

    python3 -m venv venv

Activating virtual environment

    source venv/bin/activate

You can confirm you’re in the virtual environment by checking the location of your Python interpreter:

    which python

As long as your virtual environment is activated `pip` will install packages into that specific environment, and you’ll be able
to import and use packages in your Python application.

Installing dependencies from requirements.txt
    
    python3 -m pip install -r requirements.txt

## Formatting

    black . && flake8 src/

