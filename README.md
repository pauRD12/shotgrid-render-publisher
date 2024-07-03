# Shotgrid Render Publisher (GPT4-Autofeedback)

This HDA allows you to publish your render to `Flow (Shotgun)` directly from Solaris, to continue with the USD worflow. 
Also, thanks to the `OpenAI API`, you can receive feedback notes from `GPT4`, which you can use as ideas or suggestions.
- Note: this tool only works for `single frame renders`, as GPT4 is currently only able to analyze images with its Vision module, not video.

### Prerequisites:
- Install Flow (Shotgun) API for Python [Flow API Documentation](https://support.google.com/accounts/answer/185833?hl=en)
- Install  OpenAI API for Python (Optional) [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/authentication)

### Installation:
- Download the `.hda` file and put it in your `otls` directory (on Windows, that's usually `\Documents\houdinixx.x\otls)`.
- Download the `credentials.json` file and modify it with your API keys (Check the `API Documentation` to generate the keys)
- Launch Houdini and the HDA should appear in the TAB Menu under the name `usdrender_shotgrid` (only in the LOP context).
- Demo Video: 
