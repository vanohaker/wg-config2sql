#!/bin/python3
# -*- coding: utf-8 -*-

from os import replace
import os
import re
import mysql.connector as database

wg_path = "/etc/wireguard"

def get_all_parametrs():
    peer_lines = []
    interface_lines = []
    interface_config = {}
    peer_config = {}
    for root, dirs, files in os.walk(f"{wg_path}"):
        for wg_file in files:
            with open(f'{wg_path}/{wg_file}', 'r') as fp:
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
                        name = config_lines[interface_line_num].replace('# Name = ', '').replace('\n', '')
                    elif re.match(r'^(Address = ).*', config_lines[interface_line_num]):
                        address = config_lines[interface_line_num].replace('Address = ', '').replace('\n', '')
                    elif re.match(r'^(ListenPort = ).*', config_lines[interface_line_num]):
                        listenport = config_lines[interface_line_num].replace('ListenPort = ', '').replace('\n', '')
                    elif re.match(r'^(PrivateKey = ).*', config_lines[interface_line_num]):
                        privatekey = config_lines[interface_line_num].replace('PrivateKey = ', '').replace('\n', '')
                    elif re.match(r'^(DNS = ).*', config_lines[interface_line_num]):
                        dns = config_lines[interface_line_num].replace('DNS = ', '').replace('\n', '')
                interface_config[name] = {
                    "Address" : address,
                    "ListenPort" : listenport,
                    "PrivateKey" : privatekey,
                    "DNS" : dns,
                    "wg_file" : wg_file
                }
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
                fp.close()
        return interface_config, peer_config

def mysql_connect():
    con = database.connect(
        host='localhost', 
        user = os.environ['db_username'],
        password = os.environ['db_password'],
        db = os.environ['db_name']
    )
    return con

def add_server_to_interface(interface_config):
    # check if server exist in database
    for config_data in interface_config.items():
        connect = mysql_connect()
        with connect:
            cursor = connect.cursor()
            cursor.execute(
                "INSERT INTO `interfaces`(`wg_file`, `name`, `address`, `listenport`, `privatekey`, `dns`) VALUES (%s, %s, %s, %s, %s, %s)", 
                (
                    config_data[1]['wg_file'], 
                    config_data[0], 
                    config_data[1]['Address'], 
                    config_data[1]['ListenPort'],
                    config_data[1]['PrivateKey'],
                    config_data[1]['DNS']
                )
            )
            print(f"insert server {config_data[0]}")
            connect.commit()
            connect.close()    
        
def check_interface_record(interface_config):
    result = []
    for data in interface_config.items():
        connect = mysql_connect()
        with connect:
            cursor = connect.cursor()
            cursor.execute(f"SELECT * FROM `interfaces` WHERE name='{data[0]}' AND wg_file='{data[1]['wg_file']}'")
            result.append(cursor.fetchone())
            connect.commit()
            connect.close()
    return result

if __name__ == '__main__':
    interface_config, peer_config = get_all_parametrs()
    for config in interface_config.items():
        print(f"interface_config : {config[0]} , {config[1]}")
    result = check_interface_record(interface_config)
    for res in result:
        print(f"result : {res}")

    if len(interface_config) != len(result):
        add_server_to_interface(interface_config)
