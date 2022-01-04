import configparser
import datetime
import json
import logging
import os
import re
import signal
import time
import socket
from threading import Thread
from colorama import init


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def commands():
    n = ""
    while True:
        try:
            n = input("")
            if n.isspace() or n == "":
                continue
            elif n == "{exit}":
                break
            elif n == "cls":
                cls()
                continue
            elif n == "rdlog":
                read_log()
                continue
            elif n == "cllog":
                clear_log()
                continue
            elif n == "cldata":
                clear_data()
                continue
            elif n == "help":
                _help()
                continue
            elif "ipm" in n:
                if len(n.split()) != 2:
                    print(f"{BColors.FAIL}[ERROR] Usage: ipm [mode]{BColors.ENDC}")
                else:
                    ipm(n.split()[1])
                continue
            else:
                print("\033[31m" + ('[ERROR] Unknown command ' + "\""+str(n)+"\"."+'Try help') + '\033[0m')
                continue
        except:
            print("\033[31m" + ('[ERROR] Unknown command ' + "\""+str(n)+"\"."+'Try help') + '\033[0m')
            continue
    os.kill(os.getpid(), signal.SIGTERM)


def _help():
    print(f"{BColors.OKGREEN}\nCommands: ")
    print(f"{{exit}} - Exit from program")
    print("cls - Clear the console")
    print("rdlog - Read log file")
    print("cllog - Clear log file")
    print("ipm - Change ip mode. [ip, ipp]")
    print(f"cldata - Clear data file{BColors.ENDC}\n")
    return


def ipm(mode):
    global ip_only

    if mode == "ip":
        ip_only = True
        info = "Now server is working in IP only mode"
    elif mode == "ipp":
        ip_only = False
        info = "Now server is working in IP+PORT mode"
    else:
        return print(f"{BColors.FAIL}[ERROR] Wrong mode name! Try help{BColors.ENDC}")

    return print(f"{BColors.OKGREEN}[INFO] {info}{BColors.ENDC}")


def cls():
    return os.system('cls' if os.name == 'nt' else 'clear')


def clear_data():
    try:
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(dict(), file, ensure_ascii=False, indent=4)
        print(f"{BColors.OKGREEN}[INFO] Successfully cleaned data file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def clear_log():
    try:
        open('app.log', 'w').close()
        print(f"{BColors.OKGREEN}[INFO] Successfully cleaned log file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def read_log():
    try:
        with open('app.log') as fd:
            lines = fd.readlines()
        for line in lines:
            print(line.strip())
        print(f"{BColors.OKGREEN}[INFO] Ended reading log file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def check_password(data):
    return re.fullmatch(r'^((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*]))((.)(?!\3{3})){8,26}$', data)


def check_free_port(port, rais=True):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.listen(5)
        sock.close()
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.bind(('::1', port))
        sock.listen(5)
        sock.close()
    except socket.error as e:
        if rais:
            print(f"{BColors.WARNING}[WARNING] The server is already running on port {port} {BColors.ENDC}")
            logging.warning(f"[WARNING] The server is already running on port {port}")
        return False
        # if rais:
        #     raise RuntimeError(
        #         "The server is already running on port {0}".format(port))
    return True


def read_text(name):
    content = ''
    file = open(name, 'r', encoding='utf-8')
    for line in file:
        if line.find('<img') != -1:
            z = line.split('"')
            # z[1] = os.path.join('http://localhost', z[1])
            line = ''
            for i in z:
                line += i + '"'
            line = line[0:-1]
            # print(line)
        content += line
    file.close()
    return content.encode()


def read_image(name):
    file = open(name, 'rb')
    data = file.read()
    file.close()
    return data


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print(f"{BColors.OKGREEN}[NEW CONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has connected{BColors.ENDC}")
        logging.info(f"[NEW CONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has connected")
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(client, client_address):
    try:
        if ip_only:
            address = f"{client_address[0]}"
        else:
            address = f"{client_address[0]}:{client_address[1]}"

        while True:
            date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GTM")
            msg = client.recv(BUF_SIZ).decode()

            content = msg.split('\n')[0].split(' ')[1]
            content_path = os.path.exists(os.path.join(WD, content[1:]))

            if content == "/":
                content += 'index.html'

            if content_path:
                content_type = content.split('.')[-1]
                content_file_name = content[1:]
                if content_file_name == "1.html":
                    status_code = '403 Forbidden'
                    content_file_name = '403.html'
                    content = read_text(content_file_name)
                    content_type = "text/html"
                else:
                    status_code = '200 OK'
                    if content_type in formats["text"].keys():
                        content_type = formats["text"][content_type]
                        content = read_text(content_file_name)
                    elif content_type in formats["image"].keys():
                        content_type = formats["image"][content_type]
                        content = read_image(content_file_name)
            else:
                status_code = '404 Not Found'
                content_file_name = '404.html'
                content = read_text(content_file_name)
                content_type = "text/html"

            resp = (f"HTTP/1.1 {status_code}\n"
                    f"Server: FOMCHV_Server v0.0.1\n"
                    f"Content-Type: {content_type}\n"
                    f"Content-Length: {len(content)}\n"
                    f"Date: {date}\n"
                    f"Connection: keep-alive\n"
                    f"Charset: utf-8\n"
                    f"\n")
            # print(resp)
            client.send(resp.encode() + content)

            print(f"[REQUEST {BColors.OKGREEN}{address}{BColors.ENDC} {get_timestamp()}] {content_file_name} - {status_code}")
            logging.info(f"[REQUEST {address} {get_timestamp()}] {content_file_name} - {status_code}")
    except:
        client.close()
        print(f"{BColors.WARNING}[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected{BColors.ENDC}")
        logging.info(f"[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected")
        return


def get_settings():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return int(config["Settings"]["port"]), str(config["Settings"]["working_dir"]), int(config["Settings"]["buffer_size"])


def create_config(path):
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "port", str(80))
    config.set("Settings", "working_dir", str(os.getcwd()))
    config.set("Settings", "buffer_size", str(8192))

    with open(path, "w") as config_file:
        config.write(config_file)
    config_file.close()


init()
addresses = {}
clients = {}
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

if not os.path.isfile("settings.ini"):
    create_config("settings.ini")

HOST = ''
ip_only = False
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT, WD, BUF_SIZ = get_settings()
formats = {"text": {'html': "text/html", 'css': "text/css", 'js': "text/javascript"},
           "image": {'jpg': "image/jpg", 'jpeg': "image/jpeg", 'gif': "image/gif", 'png': "image/png"}}

if check_free_port(PORT):
    SERVER.bind((HOST, PORT))
else:
    SERVER.bind((HOST, 0))

if __name__ == "__main__":

    print(f"{BColors.OKGREEN}[STARTING] Server is starting...{BColors.ENDC}")
    logging.info("[STARTING] Server is starting...")

    if ip_only:
        ip_mode_info = "Working in IP only mode"
    else:
        ip_mode_info = "Working in IP+PORT mode"

    print(f"{BColors.WARNING}[IP MODE] {ip_mode_info}{BColors.ENDC}")
    logging.info(f"[IP MODE] {ip_mode_info}")

    print(f"[BINDING] Binding address {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")
    logging.info(f"[BINDING] Binding address {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")

    print(f"[LISTENING {get_timestamp()}] Server is listening on {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")
    logging.info(
        f"[LISTENING {get_timestamp()}] Server is listening on {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")

    SERVER.listen(5)

    print("[WAITING] Waiting for connection...")
    logging.info("[WAITING] Waiting for connection...")

    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    MAIN_THREAD = Thread(target=commands)
    MAIN_THREAD.start()
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    MAIN_THREAD.join()
    SERVER.close()
