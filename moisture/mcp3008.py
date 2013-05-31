import spidev

spi = spidev.SpiDev()
spi.open(0,1)

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    r = spi.xfer2([1,(8+adcnum)<<4,0])
    adcout = ((r[1]&3) << 8) + r[2]
    return adcout

def read_pct(adcnum):
    r = readadc(adcnum)
    return int(round((r/1023.0)*100))

def read_3v3(adcnum):
    r = readadc(adcnum)
    v = (r/1023.0)*3.3
    return v

def readadc_avg(adcnum):
    r = []
    for i in range (0,10):
        r.append(readadc(adcnum))
    return sum(r)/10.0
    
def read_2Y0A02_sensor(adcnum):
    r = []
    for i in range (0,10):
        r.append(readadc(adcnum))
    a = sum(r)/10.0
    v = (a/1023.0)*3.3
    d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
    cm = int(round(d))
    return cm
