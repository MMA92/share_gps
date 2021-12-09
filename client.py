import requests
import time

def get_gps():
    try:
        resp = requests.get("http://192.168.0.73:8080/",timeout=1)
        data = resp.json()
        
    except (requests.exceptions.RequestException,ConnectionError) as E:

        if "Failed to establish a new connection" in E.args[0].args[0]:
            print("Failed to establish connection!")
        else:       
            print("error",E)

        data = None

    return data


if __name__ == "__main__":

    while 1:        
        data = get_gps()
        print(data)    
        time.sleep(1.1)