from time import sleep
import mcp3008
from controlmypi import ControlMyPi
import logging

def on_msg(conn, key, value):
    pass

logging.basicConfig(level=logging.INFO)

p = [ 
    [ ['G','moist','level',0,0,1023] ], 
    ]

conn = ControlMyPi('you@gmail.com', 'password', 'moisture', 'Moisture monitor', p, on_msg)
if conn.start_control():
    try:
        while True:
            m = mcp3008.readadc(5)
            conn.update_status({'moist':m})
            sleep(30)
    finally:
        conn.stop_control()
