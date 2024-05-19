import socket
import datetime
import struct
import logging
import time
from flask import Flask, request, jsonify, render_template
import os
import threading
from itertools import islice

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

broadcasting = False
broadcast_thread = None
tak_server_ip = '0.0.0.0'
tak_server_port = '6666'
tak_multicast_state = True
whitelisted_ssids = set()
whitelisted_macs = set()
blacklisted_ssids = {}
blacklisted_macs = {}
analysis_mode = 'realtime'  # Default mode

@app.route('/')
def index():
    return render_template('WigleToTAK.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    global tak_server_ip, tak_server_port, tak_multicast_state, analysis_mode
    tak_server_ip = data.get('tak_server_ip', tak_server_ip)
    tak_server_port = data.get('tak_server_port', tak_server_port)
    tak_multicast = data.get('takMulticast', tak_multicast_state)
    mode = data.get('mode', analysis_mode)

    if tak_server_ip and tak_server_port:
        logger.info(f"TAK Server IP and Port updated successfully. New IP: {tak_server_ip}, New Port: {tak_server_port}")
    else:
        logger.error("Missing TAK Server IP or Port in the request")

    tak_multicast_state = tak_multicast
    logger.info(f"TAK Multicast state updated successfully: {tak_multicast_state}")

    if mode in ['realtime', 'postcollection']:
        analysis_mode = mode
        logger.info(f"Analysis mode updated successfully: {analysis_mode}")
    else:
        logger.error("Invalid analysis mode in the request")

    return jsonify({'message': 'Settings updated successfully!'}), 200

@app.route('/list_wigle_files', methods=['GET'])
def list_wigle_files():
    directory = request.args.get('directory')
    if directory:
        try:
            files = [f for f in os.listdir(directory) if f.endswith('.wiglecsv')]
            sorted_files = sorted(files, reverse=True)
            return jsonify({'files': sorted_files})
        except Exception as e:
            logger.error(f"Error listing files in directory: {e}")
            return jsonify({'error': 'Error listing files in directory'}), 500
    else:
        return jsonify({'error': 'Directory parameter is missing'}), 400

@app.route('/stop_broadcast', methods=['POST'])
def stop_broadcast():
    global broadcasting, broadcast_thread
    broadcasting = False
    if broadcast_thread:
        broadcast_thread.join()  # Wait for the broadcasting thread to finish
    return jsonify({'message': 'Broadcast stopped successfully'})

@app.route('/start_broadcast', methods=['POST'])
def start_broadcast():
    global broadcasting, broadcast_thread
    data = request.json
    directory = data.get('directory')
    filename = data.get('filename')
    
    if directory and filename:
        logger.info(f'Starting broadcast for file: {filename}')
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            logger.info(f'File path: {full_path}')
            broadcasting = True  
            broadcast_thread = threading.Thread(target=broadcast_file, args=(full_path,))
            broadcast_thread.start()  # Start broadcasting in a separate thread
            return jsonify({'message': 'Broadcast started for file: ' + filename})
        else:
            return jsonify({'error': 'File does not exist'}), 404
    else:
        return jsonify({'error': 'Directory or filename parameter is missing'}), 400

@app.route('/add_to_whitelist', methods=['POST'])
def add_to_whitelist():
    data = request.json
    ssid = data.get('ssid')
    mac = data.get('mac')
    if ssid:
        whitelisted_ssids.add(ssid)
        return jsonify({'message': f'SSID {ssid} added to whitelist'})
    elif mac:
        whitelisted_macs.add(mac)
        return jsonify({'message': f'MAC address {mac} added to whitelist'})
    else:
        return jsonify({'error': 'Missing SSID or MAC address in request'}), 400

@app.route('/remove_from_whitelist', methods=['POST'])
def remove_from_whitelist():
    data = request.json
    ssid = data.get('ssid')
    mac = data.get('mac')
    if ssid:
        if ssid in whitelisted_ssids:
            whitelisted_ssids.remove(ssid)
            return jsonify({'message': f'SSID {ssid} removed from whitelist'})
        else:
            return jsonify({'error': f'SSID {ssid} not found in whitelist'}), 404
    elif mac:
        if mac in whitelisted_macs:
            whitelisted_macs.remove(mac)
            return jsonify({'message': f'MAC address {mac} removed from whitelist'})
        else:
            return jsonify({'error': f'MAC address {mac} not found in whitelist'}), 404
    else:
        return jsonify({'error': 'Missing SSID or MAC address in request'}), 400

@app.route('/add_to_blacklist', methods=['POST'])
def add_to_blacklist():
    data = request.json
    ssid = data.get('ssid')
    mac = data.get('mac')
    argb_value = data.get('argb_value')
    if ssid and argb_value:
        blacklisted_ssids[ssid] = argb_value
        return jsonify({'message': f'SSID {ssid} with ARBG value {argb_value} added to blacklist'})
    elif mac and argb_value:
        blacklisted_macs[mac] = argb_value
        return jsonify({'message': f'MAC address {mac} with ARBG value {argb_value} added to blacklist'})
    else:
        return jsonify({'error': 'Missing SSID or MAC address or ARBG value in request'}), 400

@app.route('/remove_from_blacklist', methods=['POST'])
def remove_from_blacklist():
    data = request.json
    ssid = data.get('ssid')
    mac = data.get('mac')
    if ssid:
        if ssid in blacklisted_ssids:
            del blacklisted_ssids[ssid]
            return jsonify({'message': f'SSID {ssid} removed from blacklist'})
        else:
            return jsonify({'error': f'SSID {ssid} not found in blacklist'}), 404
    elif mac:
        if mac in blacklisted_macs:
            del blacklisted_macs[mac]
            return jsonify({'message': f'MAC address {mac} removed from blacklist'})
        else:
            return jsonify({'error': f'MAC address {mac} not found in blacklist'}), 404
    else:
        return jsonify({'error': 'Missing SSID or MAC address in request'}), 400

def read_file(filename, start_position):
    with open(filename, 'r') as file:
        file.seek(start_position)
        for line in file:
            yield line.strip().split(',')

def broadcast_file(full_path, multicast_group='239.2.3.1', port=6969):
    if analysis_mode == 'realtime':
        broadcast_file_realtime(full_path, multicast_group, port)
    else:
        broadcast_file_postcollection(full_path, multicast_group, port)

def broadcast_file_realtime(full_path, multicast_group='239.2.3.1', port=6969):
    logger.info(f'Broadcasting in real-time mode for file: {full_path}')
    setup_socket_and_broadcast(full_path, multicast_group, port, chunk_size=1)

def broadcast_file_postcollection(full_path, multicast_group='239.2.3.1', port=6969, chunk_size=100):
    logger.info(f'Broadcasting in post-collection mode for file: {full_path}')
    setup_socket_and_broadcast(full_path, multicast_group, port, chunk_size)

def setup_socket_and_broadcast(full_path, multicast_group, port, chunk_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    with open(full_path, 'r') as file:
        processed_entries = set()
        while broadcasting:
            lines = list(islice(file, chunk_size))
            if not lines:
                break

            for line in lines:
                fields = line.strip().split(',')
                if len(fields) >= 10:
                    mac, ssid, authmode, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, device_type = fields[:11]
                    if (mac not in processed_entries and ssid not in processed_entries) and \
                       (not whitelisted_ssids or ssid not in whitelisted_ssids) and \
                       (not whitelisted_macs or mac not in whitelisted_macs):
                        cot_xml_payload = create_cot_xml_payload_point(mac, ssid, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, authmode, device_type)
                        if tak_multicast_state:
                            sock.sendto(cot_xml_payload.encode(), (multicast_group, port))
                        if tak_server_ip and tak_server_port:
                            sock.sendto(cot_xml_payload.encode(), (tak_server_ip, int(tak_server_port)))

                        processed_entries.add(mac)
                        processed_entries.add(ssid)
            time.sleep(0.1)
    sock.close()

def create_cot_xml_payload_point(mac, ssid, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, authmode, device_type):
    remarks = f"Channel: {channel}, RSSI: {rssi}, AltitudeMeters: {altitudemeters}, AccuracyMeters: {accuracymeters}, Authentication: {authmode}, Device: {device_type}, MAC: {mac}"
    color_argb = blacklisted_ssids.get(ssid, blacklisted_macs.get(mac, "-65281"))
    return f'''<?xml version="1.0"?>
    <event version="2.0" uid="{mac}-{firstseen}" type="b-m-p-s-m"
    time="{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.995Z')}"
    start="{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.995Z')}"
    stale="{(datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.995Z')}"
    how="m-g">
        <point lat="{currentlatitude}" lon="{currentlongitude}" hae="999999" ce="35.0" le="999999" />
        <detail>
            <contact endpoint="" phone="" callsign="{ssid}" />
            <precisionlocation geopointsrc="gps" altsrc="gps" />
            <remarks>{remarks}</remarks>
            <color argb="{color_argb}"/>
        </detail>
    </event>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)