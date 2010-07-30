#
# Development helper script 
#
# Menu: Develop > Dump Preferences
# Copyright: Twinapex Research 2009
# Author: Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>
# License: MIT
#
"""
    What we do:
    
    - Dump Eclipse preferences for development usage
    
    Note: Preferences dumped here and preferences in Preferences dialog are not in sync - see sane_settings.py
"""

from org.eclipse.core.runtime import Platform
from org.eclipse.core.resources import ResourcesPlugin

from org.eclipse.jface.dialogs import MessageDialog

__docformat__ = "epytext"

    
def dump_keys(preference):

    if len(preference.keys()) > 0:
        print "Keys:"
        for key in preference.keys():
            value = preference.get(key, None)
            print "Name: " + key + " Value:" + str(value)
    else:
        pass
        #print "No keys"

def dump_preference(preference):
    """
    
    See org.osgi.service.prefs 
    """    
        
    print preference.absolutePath() + " dumping"
    
    print preference.__class__
        
    dump_keys(preference)
        
    for child_name in preference.childrenNames():
        #print "Got:" + child_name
        
        if child_name.startswith("_") or child_name == preference.name():
            # Looks like there is magical node _SELF_
            continue
                    
        child = preference.node(child_name)
        #continue
        
        #print child.childrenNames()
        #dump_keys(child)        
        dump_preference(child)
    

service = Platform.getPreferencesService()
root = service.getRootNode()
dump_preference(root)
    

    
    
    
