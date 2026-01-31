import threading
import queue
import requests
import os

q = queue.Queue()
valid_proxies = []

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
proxy_file = os.path.join(script_dir, "proxy_list.txt")

# Open and read all the proxies
with open(proxy_file, "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)

# Check if the address works
def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            response = requests.get("http://ipinfo.io/json", 
                                    proxies={"http": proxy,
                                             "https": proxy})
        except:
            continue
        if response.status_code == 200:
            print(proxy)

            # Add to valid list
            valid_proxies.append(proxy)

# Call the checking function
threads = []
for _ in range(10):
    t = threading.Thread(target=check_proxies)
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

# Update file with only working addresses (only first 10)
with open("valid_proxies.txt", "w") as f:
    for p in valid_proxies[:10]:
        print(p)
        f.write(f'{p}\n')

print("FINISHED UPDATING PROXIES LIST")


