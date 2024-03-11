import socket
import datetime
import struct
import logging
import time
from flask import Flask, request, jsonify, render_template
import os
import threading

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

broadcasting = False
broadcast_thread = None
tak_server_ip = '0.0.0.0'
tak_server_port = '6666'
tak_multicast_state = True
whitelisted_macs = set()
blacklisted_macs = {}

@app.route('/')
def index():
    return render_template('WigleToTAK.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    global tak_server_ip, tak_server_port, tak_multicast_state
    tak_server_ip = data.get('tak_server_ip')
    tak_server_port = data.get('tak_server_port')
    tak_multicast = data.get('takMulticast')

    if tak_server_ip is not None and tak_server_port is not None:
        tak_server_ip = tak_server_ip
        tak_server_port = tak_server_port
        logger.info(f"TAK Server IP and Port updated successfully. New IP: {tak_server_ip}, New Port: {tak_server_port}")
    else:
        logging.error("Missing TAK Server IP or Port in the request")

    if tak_multicast is not None:
        tak_multicast_state = tak_multicast
        logger.info(f"TAK Multicast state updated successfully: {tak_multicast_state}")
    else:
        logging.error("Missing TAK Multicast state in the request")

    return 'Settings updated successfully!', 200

@app.route('/list_wigle_files', methods=['GET'])
def list_wigle_files():
    directory = request.args.get('directory')
    if directory:
        files = [f for f in os.listdir(directory) if f.endswith('.wiglecsv')]
        sorted_files = sorted(files, reverse=True)
        return jsonify({'files': sorted_files})
    else:
        return jsonify({'error': 'Directory parameter is missing'})

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
        # Construct full file path
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            logger.info(f'File path: {full_path}')
            broadcasting = True  
            broadcast_thread = threading.Thread(target=broadcast_file, args=(full_path,))
            broadcast_thread.start()  # Start broadcasting in a separate thread
            return jsonify({'message': 'Broadcast started for file: ' + filename})
        else:
            return jsonify({'error': 'File does not exist'})
    else:
        return jsonify({'error': 'Directory or filename parameter is missing'})

@app.route('/add_to_whitelist', methods=['POST'])
def add_to_whitelist():
    data = request.json
    mac_address = data.get('mac_address')
    if mac_address:
        whitelisted_macs.add(mac_address)
        return jsonify({'message': f'MAC address {mac_address} added to whitelist'})
    else:
        return jsonify({'error': 'Missing MAC address in request'})

@app.route('/remove_from_whitelist', methods=['POST'])
def remove_from_whitelist():
    data = request.json
    mac_address = data.get('mac_address')
    if mac_address:
        if mac_address in whitelisted_macs:
            whitelisted_macs.remove(mac_address)
            return jsonify({'message': f'MAC address {mac_address} removed from whitelist'})
        else:
            return jsonify({'error': f'MAC address {mac_address} not found in whitelist'})
    else:
        return jsonify({'error': 'Missing MAC address in request'})

@app.route('/add_to_blacklist', methods=['POST'])
def add_to_blacklist():
    data = request.json
    mac_address = data.get('mac_address')
    argb_value = data.get('argb_value')
    if mac_address and argb_value:
        blacklisted_macs[mac_address] = argb_value
        return jsonify({'message': f'MAC address {mac_address} with ARBG value {argb_value} added to blacklist'})
    else:
        return jsonify({'error': 'Missing MAC address or ARBG value in request'})

@app.route('/remove_from_blacklist', methods=['POST'])
def remove_from_blacklist():
    data = request.json
    mac_address = data.get('mac_address')
    if mac_address:
        if mac_address in blacklisted_macs:
            del blacklisted_macs[mac_address]
            return jsonify({'message': f'MAC address {mac_address} removed from blacklist'})
        else:
            return jsonify({'error': f'MAC address {mac_address} not found in blacklist'})
    else:
        return jsonify({'error': 'Missing MAC address in request'})

def read_file(filename, start_position):
    with open(filename, 'r') as file:
        file.seek(start_position)
        for line in file:
            yield line.strip().split(',')

def broadcast_file(full_path, multicast_group='239.2.3.1', port=6969):
    logger.info(f'Broadcasting COT XML packets for file: {full_path}')
    logger.info(f'Multicast group: {multicast_group}, Port: {port}')
    if tak_multicast_state:
        logger.info(f'Sending packets to multicast group: {multicast_group}, Port: {port}')
    else:
        logger.info(f'Multicast disabled. Not sending packets to multicast.')
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout for the socket
    sock.settimeout(0.2)

    # Create a multicast TTL value
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    last_position = 0
    processed_macs = set()
    while broadcasting:
        logger.debug(f"Broadcasting CoT XML packets from file: {full_path}, last position: {last_position}")
        for fields in read_file(full_path, last_position):
            if len(fields) >= 10:
                mac, ssid, authmode, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, device_type = fields[:11]
                if mac not in processed_macs and (not whitelisted_macs or mac not in whitelisted_macs):
                    cot_xml_payload = create_cot_xml_payload_point(mac, ssid, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, authmode, device_type)
                    logger.debug(f"Sending CoT XML packet: {cot_xml_payload}")
                    # Send the CoT XML packet
                    if tak_multicast_state:
                        # Send to multicast if multicast is enabled
                        sock.sendto(cot_xml_payload.encode(), (multicast_group, port))
                    
                    if tak_server_ip and tak_server_port:
                        # Send to user-defined IP and Port if available
                        sock.sendto(cot_xml_payload.encode(), (tak_server_ip, int(tak_server_port)))

                    processed_macs.add(mac)  # Add MAC address to processed set
        # Update the last position
        last_position = os.path.getsize(full_path)
        time.sleep(0.1)
        
    # Close the socket
    sock.close()

def create_cot_xml_payload_point(mac, ssid, firstseen, channel, rssi, currentlatitude, currentlongitude, altitudemeters, accuracymeters, authmode, device_type):
    remarks = f"Channel: {channel}, RSSI: {rssi}, AltitudeMeters: {altitudemeters}, AccuracyMeters: {accuracymeters}, Authentication: {authmode}, Device: {device_type}, MAC: {mac}"
    
    color_argb = blacklisted_macs.get(mac, "-65281")
    
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
