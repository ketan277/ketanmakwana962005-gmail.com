# Anthropic Blender Connector: Step-by-Step Guide

This repository contains instructions for setting up and using the Anthropic Blender Connector to accelerate your 3D production workflow using Claude and the Model Context Protocol (MCP).

## Part 1: Preparation

### Prerequisites
- **Blender:** version 3.5 or later.
- **Hardware:** At least 16GB RAM and a modern GPU.
- **Python:** version 3.10 (comes pre-installed with Blender).

### Environment Setup
1. Open your terminal or command prompt.
2. Clone the MCP repository (Replace `<URL>` with the official GitHub URL):
   ```bash
   git clone <URL>
   cd blender-mcp
   ```
3. Run the provided installation script (usually `install.py` or `setup.sh`):
   ```bash
   # If it's a Python script:
   python install.py

   # Or using the modern 'uv' package manager (recommended):
   uvx blender-mcp
   ```

#### Windows Users (PowerShell)
If you are using Windows, make sure to use **PowerShell** for environment setup commands.
To add `uv` to your PATH, run these in PowerShell:
```powershell
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

4. Open Blender and go to `Edit` > `Preferences` > `Add-ons`.
5. Search for "MCP" and enable the add-on.
6. **Restart Blender** to ensure the MCP server loads correctly.

---

## Part 2: Connecting Claude to Blender

### 1. Configure Claude Desktop
You must add the MCP server configuration to your `claude_desktop_config.json` file.

**File Location:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows Troubleshooting: "Location not available"
If you see an error saying `%APPDATA%\Claude\` is unavailable, it means the folder hasn't been created yet. This usually happens if Claude Desktop is not installed.

1. **Install Claude Desktop:** Download and install it from [claude.ai/download](https://claude.ai/download).
2. **Manual Creation (PowerShell):** If the folder is still missing, run these commands in PowerShell to create it and the config file:
   ```powershell
   # Create the directory
   New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"

   # Create an empty config file if it doesn't exist
   $configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
   if (-not (Test-Path $configPath)) {
       '{}' | Out-File -FilePath $configPath -Encoding utf8
   }
   ```

**Add this to the `claude_desktop_config.json` file:**
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

### 2. Connect in the Interface
1. **Launch Claude:** Open your Claude interface.
2. **Accept Permissions:** When the MCP permission popup appears, click "Accept".
3. **Select Project Folder:** Choose the folder where your Blender project is located. This will generate a secure token.
4. **Link Session:** In Claude's prompt window, type the following command:
   ```text
   !mcp connect --project <your_project_path>
   ```
5. **Verify Connection:** Test the link by typing:
   ```text
   !mcp list objects
   ```

---

## Part 3: Effective Prompting

To get the best results, use descriptive "Plain-English" prompts.

- **Example:** "Create a medieval stone tower, 12m tall, with moss-covered walls and a torch-lit entrance."
- **Iteration:** Add constraints one at a time (e.g., "add intricate carvings around the doorway").
- **Units:** Use metric units (meters, centimeters) for consistency.
- **Materials:** Specify texture cues like "weathered bronze" or "polished marble".

---

## Part 4: Troubleshooting and Maintenance

- **Mesh Cleanup:** Always run a quick mesh check after generation (`Mesh` > `Clean Up` > `Delete Loose`).
- **Connection Issues:** Ensure port **5000** is open and not blocked by a firewall.
- **Token Management:** Store the permission token in a hidden file named `.mcp_token` to avoid re-authorizing every time.
- **Version Control:** Save incremental versions of your `.blend` files.

---

## Part 5: Advanced Workflow

For mass production, you can script a loop to feed a CSV list of prompts to Claude using:
```text
!mcp generate
```

Monitor your token consumption in the Claude dashboard to manage costs.
