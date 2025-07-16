import connect
import time

try:
    c = connect.init_connection()
    
    print(c)
    c.send("hello!")
    while True:
        print(c.receive())
        time.sleep(1)

    c.close()

except Exception as e:
    print(e)
    exit(1)


