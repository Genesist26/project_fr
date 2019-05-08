def getMAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
        str = str.replace(':', '')
        str = '0x' + str
    except:
        str = "00:00:00:00:00:00"

    return str[0:17]


print(getMAC('wlan0'))
