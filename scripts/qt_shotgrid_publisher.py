# Stdlib modules
import json

# Third-party modules
from PySide2 import QtCore, QtGui, QtWidgets
import shotgun_api3
import hou

hda = hou.pwd().parent().parent()

# Read image path and resolution from render settings.
image_path = hou.node(hou.pwd().parm("path").eval()).parm("picture").evalAsString()
res = hou.node(hou.pwd().parm("path").eval()).parmTuple("resolution").eval()

def sg_header():
    """ Connect to Shotgrid's API """
    
    # Read credentials from .json file.
    path = hda.parm("creds").evalAsString()
    open_file = open(path)
    creds = json.load(open_file)  
    
    # Connect to Shotgun API using credentials.
    sg = shotgun_api3.Shotgun(creds["shotgun"]["website"], 
                              script_name= creds["shotgun"]["script_name"],
                              api_key= creds["shotgun"]["api_key"])
    return sg

   
def show_dialog():
    """Dialog window to visualize and publish the render in Shotgrid."""

    # Create a Qt dialog window.
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Render Output")
        
    # Create a QLabel to display the rendered image.
    img_label = QtWidgets.QLabel(dialog)
    img = QtGui.QPixmap(image_path)
    img = img.scaled(res[0]*0.75,res[1]*0.75, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    img_label.setPixmap(img)
    img_label.setAlignment(QtCore.Qt.AlignCenter)
    
    # Create a QPushButton for publishing to Shotgrid.
    button1 = QtWidgets.QPushButton("Publish to Shotgrid", dialog)
    button1.setMinimumSize(80, 50)
    # Set font for size.
    font = QtGui.QFont()
    font.setPointSize(16)
    button1.setFont(font)
    # Connect button click to publish function.
    button1.clicked.connect(lambda: publish(dialog))
    
    # Create a QLabel for displaying notes.
    notes_label = QtWidgets.QLabel()
    notes = hda.parm("gpt_notes").evalAsString()
    notes_label.setText(notes)
    notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    # Set font for size.
    font = QtGui.QFont()
    font.setPointSize(20)
    notes_label.setFont(font)
    
    # Create main layout.
    layout = QtWidgets.QVBoxLayout(dialog)    
    
    # TABS.
    tabs = QtWidgets.QTabWidget()
    layout.addWidget(tabs)
    
    # Create tab1.
    tab1 = QtWidgets.QWidget()
    tab1_lyt = QtWidgets.QVBoxLayout()
    tab1.setLayout(tab1_lyt)     
    tabs.addTab(tab1, "Render View")
    
    # Create tab2.
    tab2 = QtWidgets.QWidget()
    tab2_lyt = QtWidgets.QVBoxLayout()
    tab2_lyt.setContentsMargins(40,20,20,20)
    tab2.setLayout(tab2_lyt)        
    tabs.addTab(tab2, "GPT4 Vision Feedback")   
    
    # Add widgets to layouts.
    tab1_lyt.addWidget(img_label)   
    tab2_lyt.addWidget(notes_label)
    layout.addWidget(button1)
    
    # Execute the dialog window.
    dialog.exec_()
    
    
def publish(dialog):
    """Publish render to Shotgrid as a new Version of the selected Shot."""

    # Connect to shotgrid API.
    sg = sg_header()
     
    # Read selected project id.
    projects_menu = hda.parm("projects_menu")
    project_index = projects_menu.eval()
    project_id = projects_menu.menuItems()[project_index]
    project_id = int(project_id)
    
    # Read selected shot id.
    shots_menu = hda.parm("shots_menu")
    index = shots_menu.eval()
    shot_id = shots_menu.menuItems()[index]
    shot_id = int(shot_id)

    # Read description and notes from parameters.
    description = hda.parm("gpt_description").evalAsString()
    notes = hda.parm("gpt_notes").evalAsString()

    # Create new version.
    version_data = {
        "project": {"type": "Project", "id": project_id},
        "entity": {'type': 'Shot', 'id': shot_id},
    }
    version = sg.create("Version", version_data)
    
    # Update version info: render image and desciption.
    data = {
        "description": description,
        "image": image_path,
    }     
    sg.update("Version", version["id"], data)
    
    # Create notes with GPT4 content.
    note_data = { 
        "project": {"type": "Project", "id": project_id},
        "subject": "GPT4 feedback notes",
        "note_links": [{'type': 'Version', 'id': version["id"]}],
        "content": notes,
    }    
    sg.create("Note", note_data)
    
    # Print message when the render is published.
    print("Published to Shotgrid")
    
    # Close window after publishing.
    dialog.accept()  

# Run dialog window on the main thread.
work_item.node.scheduler.runOnMainThread(True, show_dialog)