from time import sleep
import mcp3008
from controlmypi import ControlMyPi
import logging
import datetime

def on_msg(conn, key, value):
    pass

def append_chart_point(chart, point):
    if len(chart) >= 10:
        del chart[0]
    chart.append(point)
    return chart

logging.basicConfig(level=logging.INFO)

p = [ 
    [ ['G','moist','% level',0,0,100], ['LC','chart1','Time','Value',0,100] ], 
    ]

c1 = []

conn = ControlMyPi('you@gmail.com', 'password', 'moistcmp2', 'Moisture monitor 2', p, on_msg)
if conn.start_control():
    try:
        while True:
            dt = datetime.datetime.now().strftime('%H:%M:%S')
            m = mcp3008.read_pct(5)                
            c1 = append_chart_point(c1, [dt, m])
            conn.update_status({'moist':m,'chart1':c1})
            sleep(30)
    finally:
        conn.stop_control()
