import json
import socket


class YeelightBulb:

    brightness = 0
    rgb = (0,0,0)
    current_command_id = 0
    state = 1
    ct = 1700
    support_color_temp = False
    support_rgb = False

    def __init__(self, ipaddr, port=55443):
        self.ipaddr = ipaddr
        self.port = port
        self.refreshState()

    def next_cmd_id(self):
        self.current_command_id += 1
        return self.current_command_id

    def operate_on_bulb(self, method, params):
        '''
      Operate on bulb; no gurantee of success.
      Input data 'params' must be a compiled into one string.
      E.g. params="1"; params="\"smooth\"", params="1,\"smooth\",80"
      '''

      # if idx not in bulb_idx2ip:
      #  print("error: invalid bulb idx")
      #  return

        bulb_ip = self.ipaddr
        port = self.port
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ('connect ', bulb_ip, port, '...')
            tcp_socket.connect((bulb_ip, int(port)))
            msg = '{"id":' + str(self.next_cmd_id()) + ',"method":"'
            msg += method + '","params":[' + params + ']}\r\n'
            tcp_socket.send(msg.encode())
            data = tcp_socket.recv(4096)
            tcp_socket.close()
            return data.decode()
        except Exception as e:
            print ('Unexpected error:', e)

    def refreshState(self):
        try:
            data = json.loads(self.operate_on_bulb('get_prop', '"power", "bright", ""model"'))
        except (TypeError, ValueError) as e:
                print ('Unexpected error:', e)
                return

        self.brightness = round(int(data['result'][1]) / 100 * 255)
        if data['result'][0] == 'on':
            self.state = 1
        else:
            self.state = 0

        if "set_rgb" in data['result']['model']:
            self.support_rgb = True
        if "set_ct_abx" in data['result']['model']:
            self.support_color_temp = True




    def isOn(self):
        if self.state == 0:
            return False
        if self.state == 1:
            return True

    def turnOn(self, transtime, effect="sudden"):
        self.state = 1
        self.operate_on_bulb('set_power', '"on","' + effect 
                            + '",' + str(transtime))

    def turnOff(self, transtime, effect="sudden"):
        self.state = 0
        self.operate_on_bulb('set_power', '"off","' + effect 
                            + '",' + str(transtime))

    def setBrightness(self, brightness, transtime):
        self.brightness = brightness
        self.operate_on_bulb('set_bright', str(round(self.brightness
                             / 255 * 100)) + ',"smooth",'
                             + str(transtime))

    def setRgb(self, rgb, transtime):
        self.rgb = rgb
        rgb_value = (rgb[0]*65536)+(rgb[1]*256)+rgb[2]
        self.operate_on_bulb('set_rgb', str(rgb_value) + ',"smooth",'
                             + str(transtime))

    def setColorTemp(self, ct, transtime):
        self.ct = ct
        ct_value = round((10**6)/ct)
        self.operate_on_bulb('set_ct_abx', str(ct_value) + ',"smooth",'
                             + str(transtime))
