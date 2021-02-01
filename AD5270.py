# SPI test code for AD5270BRMZ-20
import time
import spidev

spi_bus = 0                                              # SPI0
spi_device_select = 0                                    # CE0

spi = spidev.SpiDev()
spi.open(spi_bus, spi_device_select)
spi.max_speed_hz = 50000                                # Datasheet p7
spi.mode = 1                                            # CPOL = 0, CPHA = 1 (Datasheet p7)
spi.lsbfirst = False                                    # Datasheet p18

MAX_RESISTANCE      = 20000.0
WRITE_CTRL_REG      = 0x1C
READ_CTRL_REG       = 0x20
WRITE_RDAC          = 0x04
READ_RDAC           = 0x08
RDAC_WRITE_PROTECT  = 0x02

def AD5270_CalcRDAC(resistance):
    return int((resistance / MAX_RESISTANCE) * 1024.0)

def AD5270_ReadReg(command):
    data = [(command & 0x3C), 0]
    r = spi.xfer2(data)
    data = [0x00, 0x00]
    r2 = spi.xfer2(data)
    result = r2[0]
    result = (result << 8) | r2[1]
    return result

def AD5270_WriteReg(command, value):
    ui16Command = (command & 0x3C) << 8 | (value & 0x3FF)
    data = [(ui16Command >> 8) & 0xFF, ui16Command & 0xFF]
    spi.xfer2(data)

def AD5270_ReadRDAC():
    RDAC_val = AD5270_ReadReg(READ_RDAC)
    RDAC_val &= 0x03FF
    return ((RDAC_val) * MAX_RESISTANCE) / 1024.0

def AD5270_WriteRDAC(resistance):
    RDAC_val = AD5270_CalcRDAC(resistance)
    spi.xfer2([WRITE_CTRL_REG, RDAC_WRITE_PROTECT])
    AD5270_WriteReg(WRITE_RDAC, RDAC_val);
    return ((RDAC_val * MAX_RESISTANCE) / 1024.0)

while(1):
    R = float(input("R_pot ?                          >"))
    if R < 0:
        print("Exit")
        break;
    else:
        AD5270_WriteRDAC(R)
        print("Value written : " + str(AD5270_ReadRDAC()) + " Ohm")
spi.close()
