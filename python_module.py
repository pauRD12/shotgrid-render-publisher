import shotgun_api3
import json

def sg_header():
    """ Connect to Shotgrid's API """
    
    # read credentials from .json file
    path = hou.pwd().parm("creds").evalAsString()
    open_file = open(path)
    creds = json.load(open_file)  
    
    # connect to Shotgun API using credentials
    sg = shotgun_api3.Shotgun(creds["shotgun"]["website"], 
                              script_name= creds["shotgun"]["script_name"],
                              api_key= creds["shotgun"]["api_key"])
    return sg
  
def update_shots(node):
    """Populate menu with Shotgrid shots from selected sequence."""
    
    # only execute when toggle is activated
    if node.parm("sg").eval() == 1:
        try:
            # connect to Shotgun API
            sg = sg_header()
            
            # get selected sequence ID from the sequences menu
            index = node.parm("sequences_menu").eval()
            sequence_id = node.parm("sequences_menu").menuItems()[index]
            sequence_id = int(sequence_id)
            
            # define filters to find shots belonging to the selected sequence
            filters = [["sg_sequence", "is", {"type": "Sequence", "id": sequence_id}]]           
            shots = sg.find("Shot", filters, fields=["code"])
            
            # create lists for shot names and IDs
            shot_names = [shot["code"] for shot in shots]
            shot_ids = [str(shot["id"]) for shot in shots]
            
            # Get the HDA definition and parameter template group
            hda = node.type().definition()
            t_group = hda.parmTemplateGroup()
            
            # get the parameter template for the shots menu
            t_parm = node.parm("shots_menu").parmTemplate()
            
            # set the menu items (IDs) and labels (names) for the projects menu
            t_parm.setMenuItems(shot_ids)
            t_parm.setMenuLabels(shot_names)
            
            # replace the old parameter template with the updated one
            t_group.replace("shots_menu", t_parm)
            
            # update the HDA with the new parameter template group
            hda.setParmTemplateGroup(t_group)
            
        except:
            pass
        
def update_sequences(node):
    """Populate menu with Shotgrid sequences from selectes project."""

    # only execute when toggle is activated
    if node.parm("sg").eval() == 1:
        try:
            # connect to Shotgun API
            sg = sg_header()
            
            # get selected project id
            index = node.parm("projects_menu").eval()
            project_id = node.parm("projects_menu").menuItems()[index]
            project_id = int(project_id)
            
            # define filters to find sequences belonging to the selected project
            filters = [["project", "is", {"type": "Project", "id": project_id}]]          
            sequences = sg.find("Sequence", filters, fields=["code"])
            
            # create lists for sequence names and IDs
            sequence_names = [seq["code"] for seq in sequences]
            sequence_ids = [str(seq["id"]) for seq in sequences]
           
            # get the HDA definition and parameter template group
            hda = node.type().definition()           
            t_group = hda.parmTemplateGroup()  
            
            # get the parameter template for the shots menu
            seq_parm = node.parm("sequences_menu").parmTemplate()
            
            # set the menu items (IDs) and labels (names) for the psequences menu
            seq_parm.setMenuItems(sequence_ids)
            seq_parm.setMenuLabels(sequence_names)
            
            # replace the old parameter template with the updated one
            t_group.replace("sequences_menu", seq_parm)
            
            # update the HDA with the new parameter template group
            hda.setParmTemplateGroup(t_group)  
            
        except:
            pass

def update_projects(node):
    """Populate menu with Shotgrid projects."""

    # only execute when toggle is activated
    if node.parm("sg").eval() == 1:
        try:
            # connect to Shotgun API
            sg = sg_header()
            
            # search all projects from Shotgrid
            projects = sg.find("Project", filters=[], fields=["name"])
            
            # create lists for projects names and IDs
            project_names = [project["name"] for project in projects]
            project_ids = [str(project["id"]) for project in projects]
            
            # get the HDA definition and parameter template group
            hda = node.type().definition()
            t_group = hda.parmTemplateGroup()
            
            # get the parameter template for the projects menu
            t_parm = node.parm("projects_menu").parmTemplate()
            
            # set the menu items (IDs) and labels (names) for the projects menu
            t_parm.setMenuItems(project_ids)
            t_parm.setMenuLabels(project_names)
            
            # replace the old parameter template with the updated one
            t_group.replace("projects_menu", t_parm)
            
            # update the HDA with the new parameter template group
            hda.setParmTemplateGroup(t_group)    
        
        except:
            pass