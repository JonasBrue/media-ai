# media-ai

A brief description of the project goes here.

## Requirements

- Windows 10 or higher
- Python 3.8 or higher
- [ffmpeg](https://ffmpeg.org/)

## Setup

Follow these steps to set up the project on your local machine:

__1. Clone and open the repository:__

```bash
git clone https://github.com/JonasBrue/media-ai.git
cd media-ai
```

__2. Create the Virtual Environment:__

```bash
python -m venv media-ai-venv
```

__3. Activate the Virtual Environment:__

```bash
.\media-ai-venv\Scripts\activate
```

__4. Verify the Virtual Environment Activation:__

Run the following command to verify that you are in the virtual environment:
```bash
python -c "import sys; print(sys.prefix)"
```
The output should include "media-ai-venv" at the end. If not, refer to the Troubleshooting section 1.

__4. Install the dependencies:__

```bash
pip install -r requirements.txt
```

__5. Set the environment variables:__

Edit the .env file and add your API key.
OPENAI_API_KEY=your_openai_api_key_here

__6. Execute the script:__

```bash
python main.py
```

## Troubleshooting

__1. Virtual Environment Activation Failed:__

For PowerShell, you might need to adjust the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate using the command in Step 3. or this command:
```powershell
.\media-ai-venv\Scripts\Activate.ps1
```
If you still encounter issues, try using the Command Prompt (cmd.exe) instead of PowerShell.