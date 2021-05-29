#!/bin/python3
from os import replace
import re

def get_all_parametrs():
    peer_lines = []
    interface_lines = []
    interface_config = {}
    peer_config = {}
    with open('/etc/wireguard/wg0.conf', 'r') as fp:
        config_lines = fp.readlines()
        for index, line in enumerate(config_lines):
            if "[Interface]" in line:
                interface_lines.append(index)
            if "[Peer]" in line:
                peer_lines.append(index)
            if "# END" in line:
                peer_lines.append(index)
        # Interface parse
        for interface_line_num in range(interface_lines[0]+1, peer_lines[0]-1):
            if re.match(r'^(# Name = ).*', config_lines[interface_line_num]):
                wg_interface_hostname = config_lines[interface_line_num].replace('# Name = ', '').replace('\n', '')
                if len(interface_config) == 0:
                    interface_config[wg_interface_hostname] = {}
            elif re.match(r'^(Address = ).*', config_lines[interface_line_num]):
                interface_config[wg_interface_hostname]["Address"] = config_lines[interface_line_num].replace('Address = ', '').replace('\n', '')
            elif re.match(r'^(ListenPort = ).*', config_lines[interface_line_num]):
                interface_config[wg_interface_hostname]["ListenPort"] = config_lines[interface_line_num].replace('ListenPort = ', '').replace('\n', '')
            elif re.match(r'^(PrivateKey = ).*', config_lines[interface_line_num]):
                interface_config[wg_interface_hostname]["PrivateKey"] = config_lines[interface_line_num].replace('PrivateKey = ', '').replace('\n', '')
            elif re.match(r'^(DNS = ).*', config_lines[interface_line_num]):
                interface_config[wg_interface_hostname]['DNS'] = config_lines[interface_line_num].replace('DNS = ', '').replace('\n', '')
        # parse all pears section
        for peer_line_num in range(peer_lines[0], peer_lines[-1]):
            if re.match(r'^(# Name =).*', config_lines[peer_line_num]):
                wg_peer_name = config_lines[peer_line_num].replace('# Name = ', '').replace('\n', '')
                if len(peer_config) == 0:
                    peer_config[wg_peer_name] = {}
                else: 
                    peer_config[wg_peer_name] = {}
            elif re.match(r'^(PublicKey = ).*', config_lines[peer_line_num]):
                peer_config[wg_peer_name]["PublicKey"] = config_lines[peer_line_num].replace('PublicKey = ', '').replace('\n', '')
            elif re.match(r'^(AllowedIPs = ).*', config_lines[peer_line_num]):
                peer_config[wg_peer_name]["AllowedIPs"] = config_lines[peer_line_num].replace('AllowedIPs = ', '').replace('\n', '')            
        # test section
        print(interface_config)
        for data in peer_config.items():
            print(data)
        fp.close()

def gethash():
    pass

def main():
    print("123")

if __name__ == '__main__':
    get_all_parametrs()