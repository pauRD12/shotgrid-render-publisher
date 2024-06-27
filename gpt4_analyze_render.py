from openai import OpenAI
import base64
import hou
import json

# read credentials from .json file
hda = hou.pwd().parent().parent()
path = hda.parm("creds").evalAsString()
open_file = open(path)
creds = json.load(open_file) 

# Extract the OpenAI API key from the credentials
OPEN_AI_KEY = creds["open_ai_key"]

# Retrieve the image path from the Houdini node parameters
image_path = hou.node(hou.pwd().parm("path").eval()).parm("picture").evalAsString()

class GPT4RenderAnalyzer():

    def __init__(self):
        """ Initialize the OpenAI client with the provided API key. """
        self.client = OpenAI(api_key=OPEN_AI_KEY)

    def encode_image(self, image_path):
        """ Function to encode the image in base64 format. """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_render(self, image_path): 
        """ Analyze render using GPT4 Vision."""  

        # Encode the image to base64 string
        base64_image = self.encode_image(image_path)

        # Create the messages payload for the OpenAI API call
        messages = [
            {"role": "system", "content":  hda.parm("system_prompt").evalAsString()},
            {"role": "user", "content": [
                    {"type": "text", "text": hda.parm("user_prompt").evalAsString()},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            },
          ]

        # Make the API call to OpenAI to get the response
        completion = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages = messages,
            max_tokens=150,
        )

        # Extract and return the response text from the API response
        response = completion.choices[0].message.content.strip()
        return response

# Analyze the render and get the notes       
notes = GPT4RenderAnalyzer().analyze_render(image_path)

# Set the analysis notes back to the HDA parameter
hda.parm("gpt_notes").set(notes)
