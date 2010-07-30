"""

    Find out all about devices in local ethernet / WLAN and Bluetooth

"""


import bluetooth, ethernet

def scan_all():
    """
    Start WLAN and Bluetooth scan in parallel.
    """
    
    
    device_data = bluetooth_devices + ethernet_devices
    

    return device_data

def create_context_info():
    
    bluetooth_info = bluetooth.get_local_info()
    
    ethernet_info = ethener.get_local_info()

    ip_info = get_local_ip_data()
    
    
    device_data = scan_all()

    bluetooth_devices = bluetooth.scan_bluetooth()
    ethernet_devices = ethernet.scan_ethernet()
    
    data = {
            "local" : {
                 "bluetooth" : bluetooth_info,
                 "ethernet" : ethernet_info,
                 "ip" : ip_info,
            },
            
            "reachable" : {
                   "ethernet" : ethernet_devices,
                   "bluetooth" : bluetooth_devices
             }
    }
    
    
    
