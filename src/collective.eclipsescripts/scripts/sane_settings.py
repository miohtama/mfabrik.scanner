#
# Set Eclipse preferences according to Plone development best practices 
#
# NOTE: Aptana Installation assumed
#
# Menu: Plone > Set Plone Preferences
# Copyright: Twinapex Research 2009
# Author: Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>
# License: MIT
#
"""
    What we do:
    
    1. Set save tabs as spaces, tab width 8 spaces 
    
    2. Add .egg-info, .pydevproject and .project to SVN ignore list
    
    3. Associate various Aptana editors with Zope related file types
"""

import re
import sys
from xml.dom import minidom

from org.eclipse.core.runtime import Platform
from org.eclipse.core.resources import ResourcesPlugin

from org.eclipse.jface.dialogs import MessageDialog

def get_preference(path, key, default=None):
    """
    """
    service = Platform.getPreferencesService()
    root = service.getRootNode()
    pref = root.node(path)
    return pref.get(key, default)

def set_preference(path, key, value, type="string"):
    """ Set a preference.
    
    http://help.eclipse.org/galileo/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/runtime/preferences/package-summary.html
    
    NOTE: Workbench must be restarted to make changes effective - 
    looks like Preference dialog keeps its own cached copy of preference somewhere and ignores changes here.  
    """
    service = Platform.getPreferencesService()
    root = service.getRootNode()
    pref = root.node(path)    

    # Java and static typing bites here...
    if type=="string":
        pref.put(key, value)
    elif type=="boolean":
        pref.putBoolean(key, value)
    elif type=="integer":
        pref.putInt(key, value)
    else:
        raise RuntimeError("Unknown type:" + type)
    
    pref.flush()
    
def add_ignore_mask(mask):
    """ Ignore certain files from the version control.
    
    This is not nice as we poke the internal preference storage format.
            
    @param mask: String what to ignore, example "setup.cfg" or "*.myfiles"
    """
    pref = "instance/org.eclipse.team.core"
    key = "ignore_files"
    
    # value is line pairs
    # first line = mask
    # second line = if enabled "true" or "false"
    value = get_preference(pref, key, default="")
    print "Got ignored files:" + value
    print "---"
 
    if not mask in value:
        value += mask + "\n"
        value += "true\n"
    
    set_preference(pref, key, value)
    
def dont_fuck_up_tabs():
    """    
    Ah. I love how Eclipse developers decided to go against the whole other world by redefining the tab width.
    
    The change here, of course, messes up everything if you try to read Java source code. 
    But who would want to work with Java????
    
    The function name must go hand in hand with the annoyance of this feature. 
    """    
    set_preference("instance/org.eclipse.ui.editors", "spacesForTabs", True, type="boolean")
    set_preference("instance/org.eclipse.ui.editors", "tabWidth", 8, type="integer")


def parse_editors_xml(xml):
    """


    The data is something like::
        <editors version="3.1">
            <info extension="py" name="*">
            <editor id="org.python.pydev.editor.PythonEditor"/>
            <defaultEditor id="org.python.pydev.editor.PythonEditor"/>
            </info>
            <info extension="yml" name="*">
            <editor id="com.aptana.ide.editors.YMLEditor"/>
            <defaultEditor id="com.aptana.ide.editors.YMLEditor"/>
            </info>
    """
    doc = minidom.parseString(xml)
    
    root = doc.documentElement
    assert root.tagName == "editors", "Unknown file association storage format type"  
    assert root.getAttribute("version") == "3.1", "Unknown file association storage format version"
    
    return doc


def get_association(doc, extension):
    """
    
    
    @param doc: DOM of editors XML 
    """
    infos = doc.getElementsByTagName("info")
    for info in infos:
        if info.getAttribute("extension") == extension:
            return info
        
    return None

def add_association(doc, extension, editor_id):
    """ Add file assocications.
    
    <info extension="py" name="*">
        <editor id="org.python.pydev.editor.PythonEditor"/>
        <defaultEditor id="org.python.pydev.editor.PythonEditor"/>
    </info>
    
    """
    info = doc.createElement("info")
    info.setAttribute("extension", extension)
    info.setAttribute("name", "*")
    
    editor = doc.createElement("editor")
    editor.setAttribute("id", editor_id)
    info.appendChild(editor)

    defaultEditor = doc.createElement("defaultEditor")
    defaultEditor.setAttribute("id", editor_id)
    info.appendChild(defaultEditor)
    
    doc.documentElement.appendChild(info)            

def associate_zope_file_types():
    """
    
    """
    pref = "instance/org.eclipse.ui.workbench"
    key = "resourcetypes"
    
    data = get_preference(pref, key)
    doc = parse_editors_xml(data)
    
    if get_association(doc, "zcml") == None:
        add_association(doc, "zcml", "com.aptana.ide.editors.XMLEditor")

    if get_association(doc, "pt") == None:
        add_association(doc, "pt", "com.aptana.ide.editors.HTMLEditor")        

    if get_association(doc, "cpt") == None:
        add_association(doc, "cpt", "com.aptana.ide.editors.HTMLEditor")        
        
    if get_association(doc, "cpy") == None:
        add_association(doc, "cpy", "org.python.pydev.editor.PythonEditor")

    # Group all *.css.dtml as CSS files here
    if get_association(doc, "dtml") == None:
        add_association(doc, "dtml", "com.aptana.ide.editors.CSSEditor")

    # Group all *.kss as CSS files here
    if get_association(doc, "kss") == None:
        add_association(doc, "kss", "com.aptana.ide.editors.CSSEditor")

    
    value = doc.documentElement.toxml()
    print "Setting editors to:" + doc.documentElement.toxml()    
    set_preference(pref, key, value)
 

def use_utf8():
    """
    Default OSX encoding is MacRoman. This fcks up things badly.
    
    /instance/org.eclipse.core.resources 
    """
    
    if get_preference("instance/org.eclipse.core.resources", "encoding", default=None) == None:
        set_preference("instance/org.eclipse.core.resources", "version", 1, type="integer")    
    
    set_preference("instance/org.eclipse.core.resources", "encoding", "UTF-8")    
 
def require_restart():
    """ Need to restart because preference changes are not reflected otherwise.
    
    TODO: There must be a smarter way...
    """
    
    query = MessageDialog.openQuestion(window.getShell(), "Eclipse restart required", "Eclipse restart is required to make changes effective. Restart now?") 

    if query:
        workbench = window.getWorkbench()
        workbench.restart();

def go():    
    """
    The stuff we ought to do
    """
    # Never ever commit egg-info, it breaks lots of stuff
    
    query = MessageDialog.openQuestion(window.getShell(), "Plone Development References Set-up", "This will modify your workspace preferences to be suitable for Plone development. For details please consult the user guide. Continue?") 

    if not query:
        return
    
    # Compiled .PO files
    # Plone will compile these on start up
    add_ignore_mask("*.mo")
    
    # Never commit EGGs. Many broken tools (paster!) 
    # populate / download eggs to source folder
    # also note that capitalization may vary  
    add_ignore_mask("*.egg-info")
    add_ignore_mask("*.egg")
    add_ignore_mask("*.EGG")
    add_ignore_mask("*.EGG-INFO")
    
    # Eclipse settings files
    add_ignore_mask(".project")
    add_ignore_mask(".pydevproject")
    
    # Following are buildout or setuptools generated folders
    add_ignore_mask("bin")
    add_ignore_mask("build")
    add_ignore_mask("develop-eggs")
    add_ignore_mask("downloads")
    add_ignore_mask("eggs")
    add_ignore_mask("fake-eggs")
    add_ignore_mask("parts")
    add_ignore_mask("dist")


    # Not entirely sure what this folder is, but this hidden
    # folder appears in Eclipse project root on OSX
    add_ignore_mask(".settings")
    
    # Following files are in nested buildouts
    add_ignore_mask(".installed.cfg")
    add_ignore_mask(".mr.developer.cfg")
    
    # Nested version control checkouts in the source tree
    add_ignore_mask(".hg")
    add_ignore_mask(".git")
    add_ignore_mask(".bzr")
    
    use_utf8()
    dont_fuck_up_tabs()
    associate_zope_file_types()
    require_restart()

try: 
    # Sanity check
    import com.aptana
    go()
except ImportError:
    MessageDialog.openInformation(window.getShell(), "Aptana Studio required", "This script works only with Aptana Studio based installation - http://www.aptana.org/" )    
    
    
    
