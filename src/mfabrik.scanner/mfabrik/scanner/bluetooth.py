import ligthblue

def scan_bluetooth():
    """ 
    @return: list of tuples ("bluetooth", addr, name, extra) 
    """
    
    devices = ligthblue.finddevices(getnames=True, length=45)
    result = []
    for device in devices:
        result.append(("bluetooth", device[0], device[1], device[2]))
    

    return result

def get_local_info():
    return (("bluetooth", lightblue.gethostaddr(), None, lightblue.gethostclass()))