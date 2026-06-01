# Anthropic Blender Connector: Step-by-Step Guide

This guide is based on the Anthropic launch of the Blender connector (Published 15th May 2026). Integrating AI into your 3D workflow can boost production throughput by 30–40%.

## Part 1: Why AI Integration Matters
Artificial intelligence can generate geometry, textures, and lighting from scene descriptions. This shrinks the iteration loop from hours to minutes, allowing artists to focus on composition.
- **Identify:** Delegate repetitive tasks like basic props to AI.
- **Measure:** Set baseline metrics for current scene creation time.
- **Pilot:** Test the connector on a small project first.

## Part 2: Preparing Your Development Environment

### Prerequisites
- **Blender:** version 3.5 or later.
- **Hardware:** At least 16GB RAM and a modern GPU.
- **SSD:** Keep the MCP folder on a fast SSD to reduce file I/O latency.
- **Python:** version 3.10 (comes pre-installed with Blender).

### Environment Setup
1. Open your terminal or command prompt.
2. Clone the MCP repository:
   ```bash
   git clone <URL>
   cd blender-mcp
   ```
3. Run the provided installation script. Using `uv` is recommended:
   ```bash
   uvx blender-mcp
   ```

#### Windows Users (PowerShell)
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

## Part 3: Connecting Claude to Blender Seamlessly

### 1. Configure Claude Desktop
Add the MCP server configuration to your `claude_desktop_config.json`.

**File Location:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration Block:**
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
1. **Launch Claude** and accept the MCP permission popup.
2. **Select Project Folder:** Choose your Blender project directory.
3. **Link Session:** In Claude's prompt window, use:
   ```text
   !mcp connect --project <path>
   ```
4. **Verify Connection:** Test with:
   ```text
   !mcp list objects
   ```
- **Pro Tip:** Store the permission token in a hidden `.mcp_token` file to avoid re-authorizing each session.
- **Troubleshooting:** Check if port **5000** is open and not blocked by a firewall.

---

## Part 4: Crafting Effective Plain-English Prompts

- **Be Specific:** "Create a medieval stone tower, 12m tall, with moss-covered walls and a torch-lit entrance."
- **Iterate:** Add one constraint at a time (e.g., "add intricate carvings around the doorway").
- **Units:** Use metric units (meters, centimeters).
- **Materials:** Specify texture cues ("weathered bronze", "polished marble").
- **Limit:** One primary object per prompt to avoid tangled geometry.
- **Quality Check:** Review mesh for non-manifold edges before committing to animation.

---

## Part 5: Avoiding Common Mistakes and Pitfalls

- **Cleanup:** AI output is not final art. Run `Mesh > Clean Up > Delete Loose` after generation.
- **Avoid Ambiguity:** Don't use vague phrases like "nice building". Be descriptive.
- **Version Control:** Save incremental `.blend` files to revert if a prompt produces unusable results.
- **Track Prompts:** Document prompt versions in a spreadsheet to track what works best.

---

## Part 6: Scaling Workflow and Future Enhancements

- **Batch Processing:** Create a CSV file of prompts and use a Python script to call `!mcp generate` for each row.
- **Stay Updated:** Newer versions will add support for animation rigs and texture baking.
- **Monitor Costs:** Check token consumption in the Claude dashboard.
- **Community:** Join the official Anthropic community forum for early access and support.
