# Anthropic Blender Connector: સ્ટેપ-બાય-સ્ટેપ માર્ગદર્શિકા

આ માર્ગદર્શિકા તમને તમારા લેપટોપમાં Anthropic Blender Connector સેટ કરવામાં મદદ કરશે.

## ભાગ ૧: તૈયારી (Preparation)

### જરૂરી વસ્તુઓ:
- **Blender:** વર્ઝન 3.5 અથવા તેનાથી નવું.
- **Hardware:** ઓછામાં ઓછી 16GB RAM અને સારું GPU.
- **Python:** વર્ઝન 3.10 (જે Blender ની સાથે જ આવે છે).

### સેટઅપ કરવાની રીત:
૧. તમારું ટર્મિનલ અથવા કમાન્ડ પ્રોમ્પ્ટ ખોલો.
૨. MCP રિપોઝિટરી ક્લોન કરો:
   ```bash
   git clone <GitHub_URL>
   cd blender-mcp
   ```
૩. ઇન્સ્ટોલેશન સ્ક્રિપ્ટ ચલાવો:
   ```bash
   uvx blender-mcp
   ```

૪. Blender ખોલો અને `Edit` > `Preferences` > `Add-ons` માં જાઓ.
૫. "MCP" સર્ચ કરો અને તેને ઇનેબલ (Enable) કરો.
૬. **Blender ફરીથી શરૂ કરો (Restart).**

## ભાગ ૨: Claude ને Blender સાથે જોડવું

### ૧. Claude ડેસ્કટોપ કોન્ફિગરેશન
તમારે `claude_desktop_config.json` ફાઇલમાં નીચે મુજબ ફેરફાર કરવા પડશે.

**ફાઇલનું સ્થાન (Location):**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

જો તમને આ ફોલ્ડર ન મળે, તો Claude Desktop એપ ઇન્સ્ટોલ કરો.

**આ કોડ ફાઇલમાં ઉમેરો:**
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

### ૨. કનેક્શન તપાસવું
૧. Claude એપ ખોલો.
૨. પરમિશન માંગે ત્યારે "Accept" આપો.
૩. Claude માં આ કમાન્ડ લખો:
   ```text
   !mcp connect --project <તમારા_પ્રોજેક્ટનો_પાથ>
   ```
૪. કનેક્શન ચેક કરવા માટે:
   ```text
   !mcp list objects
   ```

## ભાગ ૩: પ્રોમ્પ્ટિંગ (Prompting) ટીપ્સ

- ચોક્કસ ભાષાનો ઉપયોગ કરો. ઉદાહરણ: "Create a medieval stone tower, 12m tall."
- એક સાથે બધું ન કરાવો, ધીમે ધીમે ફેરફાર કરો.
- માપ માટે મીટર કે સેન્ટીમીટરનો ઉપયોગ કરો.

## ભાગ ૪: સામાન્ય ભૂલોથી બચો

- AI દ્વારા બનાવેલી વસ્તુઓને હંમેશા ચેક કરો.
- `Mesh` > `Clean Up` > `Delete Loose` નો ઉપયોગ કરો.
- તમારા કામને વારંવાર સેવ કરતા રહો.

---
વધારે માહિતી માટે [Anthropic Community Forum](https://community.anthropic.com) માં જોડાઓ.
