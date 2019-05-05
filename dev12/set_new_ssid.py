import re


def set_new_ssid(new_ssid, new_password):
    print("set_new_password()")

    global debug_on_window

    if debug_on_window:
        filepath = "D:/home/pi/project/project_fr/wpa_supplicant.conf"
    else:
        filepath = "/etc/wpa_supplicant/wpa_supplicant.conf"

    print("filepath exists")
    with open(filepath, 'r') as f:
        in_file = f.read()
        f.close()

    if not re.search(r'ssid', in_file):
        msg = "\nnetwork={\n\tssid=\"" + new_ssid + "\"\n\tpsk=\"" + new_password + "\"\n\tkey_mgmt=WPA-PSK\n}"
        out_file = in_file + msg

    out_file = re.sub(r'ssid=".*"', 'ssid=' + '"' + new_ssid + '"', out_file)
    out_file = re.sub(r'psk=".*"', 'psk=' + '"' + new_password + '"', out_file)

    with open(filepath, 'w') as f:
        f.write(out_file)
        f.close()

def add_new_ssid(new_ssid, new_password):


    '''

    BUG
    :param new_ssid:
    :param new_password:
    :return:
    '''
    print("set_new_password()")

    global debug_on_window

    if debug_on_window:
        filepath = "D:/home/pi/project/project_fr/wpa_supplicant.conf"
    else:
        filepath = "/etc/wpa_supplicant/wpa_supplicant.conf"

    print("filepath exists")
    with open(filepath, 'r') as f:
        in_file = f.read()
        f.close()

    out_file = re.sub(r'ssid=".*"', 'ssid=' + '"' + new_ssid + '"', in_file)  # change password only
    out_file = re.sub(r'psk=".*"', 'psk=' + '"' + new_password + '"', out_file)  # change password only

    print(out_file)

    with open(filepath, 'w') as f:
        f.write(out_file)
        f.close()


    # x = in_file[in_file.index('network={'):in_file.index('}')+1]

    # res = re.search('network={(.*)}', in_file)
    # print("x =>", x)
    # print("x =>", res.group(1))
    # msg = "\nnetwork={\n\tssid=\"" + new_ssid + "\"\n\tpsk=\"" + new_password + "\"\n\tkey_mgmt=WPA-PSK\n}"
    #
    # result = re.search('network={(.*)}', msg)
    # print(result)

    # print("in_file => ", in_file)

    # if re.search("ssid=\"" + new_ssid + "\"", in_file):
    #     print("Found ssid ")
    #     out_file = re.sub(r'psk=".*"', 'psk=' + '"' + new_password + '"', in_file)  # change password only
    #
    # else:
    #     print("Not found ssid")
    #     msg = "\nnetwork={\n\tssid=\"" + new_ssid + "\"\n\tpsk=\"" + new_password + "\"\n\tkey_mgmt=WPA-PSK\n}"
    #     out_file = in_file + msg
    #
    # # print("out_file => ", out_file)
    #
    # with open(filepath, 'w') as f:
    #     f.write(out_file)
    #     f.close()


debug_on_window = True

set_new_ssid('testNetwork2', '00001111')

# add_new_ssid("testNetwork-2", 'xxxxxxxx')
