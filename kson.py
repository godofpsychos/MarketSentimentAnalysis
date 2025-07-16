import random
import time

i=0
while(True):  # Example: 15 iterations
    if i % 30 == 0:
        num = random.random()
        with open("heartbeat.txt", "w") as f:
            f.write(str(num))
        time.sleep(2.5)  # Sleep for 2.5 seconds to simulate heartbeat
    i += 1