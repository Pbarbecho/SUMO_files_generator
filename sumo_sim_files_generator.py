# =========================================
# test routes generation
# developed by Pablo Barbecho Phd student
# pablo.barbecho@upc.edu
# =========================================

import os
from xml.dom import minidom
import subprocess
#import matplotlib.pyplot as plt
#import numpy as np


def net_generate(output_dir, osm_file, sumo_path, file_name):
    output_net_file = '{0}{1}.net.xml'.format(output_dir, file_name)
    os.chdir(sumo_path)
    #SUMO 1.2.0
    cmd = './netconvert -v -W --opposites.guess.fix-lengths --no-left-connections --check-lane-foes.all --junctions.join-turns --junctions.join --roundabouts.guess --no-turnarounds.tls --no-turnarounds --plain.extend-edge-shape --remove-edges.isolated --show-errors.connections-first-try --keep-edges.by-vclass passenger --ramps.guess --rectangular-lane-cut --edges.join --osm-files {0} -o {1}'.format(
    #SUMO 0.32.0
    #cmd = './netconvert -v -W --osm-files {0} -o {1}'.format(
        osm_file, output_net_file)
    return os.system(cmd)


def poly_generate(output_dir, osm_file, file_name):
    output_poly_file = "{0}/{1}.poly.xml".format(output_dir, file_name)
    output_net_file = '{0}{1}.net.xml'.format(output_dir, file_name)
    cmd = 'polyconvert -n {0} --osm-files {1} -o {2} --ignore-errors true'.format(output_net_file, osm_file,
                                                                                  output_poly_file)
    return os.system(cmd)


def program_header():
    env_sumo_var = subprocess.getoutput('printenv | grep SUMO')
    print('\n')
    print('-' * 55)
    print("SUMO files generator for urban simulations !!!")
    print('-' * 55)
    print(
        "\nInputs: \n        1) OSM file location \n        2) SUMO installation path (Environment variable {0})\n        3) Files name\n        4) Routes generation:".format(env_sumo_var))
    print(' ' * 15 + '(e) end time        end of vehicles appearance')
    print(' ' * 15 + '(p) period        - Generate vehicles with equidistant departure times')
    print(' ' * 15 + '(i) intermediate  - Generates the given number of intermediate way points')
    print(
        "\nOutputs:  *.net,   *.rou,   *.conf,   *.routes.xml,   *.flows.xml")  # PENDIENTE ESTRUCTURA XML DE routes y flows files
    return


def random_trips(output_dir, file_name, end_time, period, intermediate, path_sumo_installation_path):
    net_file = '{0}{1}.net.xml'.format(output_dir, file_name)
    output_rou_file = '{0}{1}.rou.xml'.format(output_dir, file_name)
    cmd = 'python randomTrips.py -n {0} --validate -e {1} -p {2} -i {3} --vehicle-class passenger -r {4}'.format(
        net_file, end_time, period, intermediate, output_rou_file)
    os.chdir(path_sumo_installation_path + '../tools/')
    return os.system(cmd)


def lee_rou_file(output_dir, file_name):
    rou_file = '{0}{1}.rou.xml'.format(output_dir, file_name)
    rou = minidom.parse(rou_file)
    items = rou.getElementsByTagName('route')
    route_id = 0
    flow_id = 0
    routes = []
    flows = []
    vtype = 'passenger'
    for elem in items:
        edges = str(elem.attributes['edges'].value)
        route = '   <route id="{0}" edges="{1}"/>'.format(route_id, edges)
        edges_list = edges.split()
        first_edge = edges_list[0]
        last_edge = edges_list[-1]
        flow = '   <flow id="{0}" from="{1}" to="{2}" begin="0" end="1" number="1" type="{3}" via="{4}"/>'.format(
            flow_id, first_edge, last_edge, vtype, edges)
        route_id += 1
        flow_id += 1
        routes.append(route)
        flows.append(flow)

    output_routes_file = '{0}{1}.routes.xml'.format(output_dir, file_name)
    output_flows_file = '{0}{1}.flows.xml'.format(output_dir, file_name)
    save_routes(routes, output_routes_file)
    save_flows(flows, output_flows_file)

    # replace departure time by 0.00
    depart_to_zero = 's/depart=".*"/depart="0.00"'
    cmd = "sed -i '{0}'/g {1}".format(depart_to_zero, rou_file)
    os.system(cmd)

    return route_id


def save_routes(routes, output_routes_file):
    nameHandle = open(output_routes_file, 'w')
    for num in range(len(routes)):
        nameHandle.write(routes[num] + '\n')
    nameHandle.close()


def save_flows(flows, output_flows_file):
    nameHandle = open(output_flows_file, 'w')
    for num in range(len(flows)):
        nameHandle.write(flows[num] + '\n')
    nameHandle.close()


def tail_print(output_dir, num_of_routes_generated):
    print('\n')
    print('-' * 70)
    print('  {0}   routes generated and translated to flows'.format(num_of_routes_generated))
    files_generated = os.listdir(output_dir)
    num_files = len(files_generated)  # .osm
    print('  {0}     new files generated in path: {1} '.format(num_files, output_dir))
    print('-' * 70)
    for i in files_generated:
        print(" ", i)
    print('-' * 70)


def sumo_config_file(output_dir, file_name, end_time):
    output_sumo_config_file = '{0}{1}.sumo.cfg'.format(output_dir, file_name)
    nameHandle = open(output_sumo_config_file, 'w')

    nameHandle.writelines(['<?xml version="1.0" encoding="UTF-8"?>',
                           '\n<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/sumoConfiguration.xsd">',
                           '\n    <input>',
                           '\n        <net-file value="{0}.net.xml"/>'.format(file_name),
                           '\n        <route-files value="{0}.rou.xml"/>'.format(file_name),
                           '\n        <additional-files value="{0}.poly.xml"/>'.format(file_name),
                           '\n    </input>',
                           '\n    <output>',
                           '\n         <!--<summary-output value="/root/Documents/RESULTS/2hGAR/logs/SUMO_summary_LD.out"/>-->',
                           '\n    </output>',
                           '\n    <processing>',
                           '\n        <time-to-teleport value="300"/>',
                           '\n        <time-to-teleport.highways value="0"/>',
                           '\n    </processing>',
                           '\n    <time>',
                           '\n        <begin value="0"/>',
                           '\n        <end value="{0}"/>'.format(end_time),
                           '\n        <step-length value="1"/>',
                           '\n    </time>',
                           '\n</configuration>'])
    nameHandle.close()


if __name__ == '__main__':

    program_header()
    path_osm_file = ''
    path_sumo_installation_path = ''
    file_name = ''
    end_time = 0
    period = 0
    intermediate = 0

    while True:
        try:
            path_osm_file = str(input('\n1. OSM file location (e.g. /root/Desktop/testmap.osm): '))
            if path_osm_file in ['']:
                path_osm_file = '/root/Desktop/NEW_MAP_BCN/sfamilia.osm'
            break
        except:
            continue

    while True:
        try:
            path_sumo_installation_path = str(
                input('2. SUMO installation path (e.g. /opt/sumo-0.32.0/bin/):  '))
            if path_sumo_installation_path in ['']:
                path_sumo_installation_path = '/opt/sumo-1.2.0/bin/'
            break
        except:
            continue

    while True:
        try:
            file_name = str(input('3. Files name:  '))
            if file_name in ['']:
                file_name = 'sfamilia'
            break
        except:
            continue

    print('4. Route generation:')

    while True:
        try:
            end_time = int(input(" " * 10 + '(e). END TIME       (default 7000s): '))
            break
        except:
            if end_time == 0:
                end_time = 6000
            break

    while True:
        try:
            period = int(input(" " * 10 + '(p). PERIOD         (default 1s): '))
            break
        except:
            if period == 0:
                period = 1
            break

    while True:
        try:
            intermediate = int(input(" " * 10 + '(i). INTERMEDIATE   (default 10): '))
            break
        except:
            if intermediate == 0:
                intermediate = 10
            break

    output_dir = subprocess.getoutput('dirname {0}'.format(path_osm_file)) + '/'
    net_generate(output_dir, path_osm_file, path_sumo_installation_path, file_name)
    poly_generate(output_dir, path_osm_file, file_name)
    random_trips(output_dir, file_name, end_time, period, intermediate, path_sumo_installation_path)
    num_of_routes_generated = lee_rou_file(output_dir, file_name)
    tail_print(output_dir, num_of_routes_generated)
    sumo_config_file(output_dir, file_name, end_time)
