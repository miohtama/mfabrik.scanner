#
# Menu: Plone > Edit buildout.cfg
# Copyright: Twinapex Research 2009
# Author: Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>
# License: MIT
#

import os

from java.io import File

from org.eclipse.core.runtime import Platform
from org.eclipse.core.resources import ResourcesPlugin
from org.eclipse.jface.dialogs import MessageDialog

from org.eclipse.core.filesystem import EFS;
from org.eclipse.core.filesystem import IFileStore;
from org.eclipse.ui import PartInitException
from org.eclipse.ui import IWorkbenchPage
from org.eclipse.ui import PlatformUI
from org.eclipse.ui.ide import IDE
 
__docformat__ = "epytext"

"""

http://wiki.eclipse.org/FAQ_How_do_I_open_an_editor_programmatically%3F

"""

def get_buildout_path():
    """    
    @return: Path to buildout folder - assuming Eclipse is set up according to instructions
    """         

    # workspace is org.eclipse.core.internal.resources.Workspace
    # http://help.eclipse.org/galileo/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/IWorkspace.html
    workspace = ResourcesPlugin.getWorkspace()    
    root = workspace.getRoot()
    location = root.getRawLocation()
    path = location.toOSString()
    path = os.path.join(path, "..")
    path = os.path.normpath(path)
    return path

def go():
    # IFileStore
    
    path = get_buildout_path()
    buildout = os.path.join(path, "buildout.cfg")
    fileToOpen = File(buildout)     
    fileStore = EFS.getLocalFileSystem().getStore(fileToOpen.toURI());
    # IWorkbenchPage
    page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage()
    IDE.openEditorOnFileStore( page, fileStore );


go()