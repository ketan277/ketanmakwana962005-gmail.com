# REA (Reverse Engineer Anything) ઇન્સ્ટોલેશન અને Tally Prime જેવી એપ બનાવવાની સંપૂર્ણ માર્ગદર્શિકા

આ ગાઇડમાં REA (Reverse Engineer Anything) ના ઉપયોગ અને Tally Prime જેવી એકાઉન્ટિંગ/ERP એપ્લિકેશનના દરેક ફીચરનું રિવર્સ એન્જિનિયરિંગ કરીને તમારી પોતાની એપ બનાવવાની સ્ટેપ-બાય-સ્ટેપ પદ્ધતિ સમજાવવામાં આવી છે.

---

## ભાગ ૧: REA શું છે અને તેનું સેટઅપ કેવી રીતે કરવું?

**REA (Reverse Engineer Anything)** એક શક્તિશાળી CLI અને Model Context Protocol (MCP) સર્વર છે. તે બાઈનરીઝ, ડેટાબેઝ, નેટવર્ક પ્રોટોકોલ, વેબ અને ઈલેક્ટ્રોન એપનું વિશ્લેષણ કરવામાં અને AI કોડિંગ એજન્ટ્સ (જેવા કે VS Code Cline, Cursor, Claude Code) ને રિવર્સ એન્જિનિયરિંગ ડેટા પૂરો પાડવામાં મદદ કરે છે.

### ૧. લોકલ ઇન્સ્ટોલેશન કમાન્ડ
જો તમે તમારા પોતાના કમ્પ્યુટરમાં REA ઇન્સ્ટોલ કરવા માંગતા હોવ તો ટર્મિનલમાં નીચે મુજબ રન કરો:
```bash
npm install -g rea-agents
```
તપાસો કે ટૂલ યોગ્ય રીતે ઇન્સ્ટોલ થઈ ગયું છે:
```bash
rea --version
```

### ૨. VS Code / AI Agents માં MCP તરીકે કનેક્ટ કરવું

#### VS Code (Claude Dev / Cline / Roo Code):
તમારા MCP સેટિંગ્સ (`cline_mcp_settings.json` અથવા VS Code MCP settings) માં નીચે મુજબ ઉમેરો:
```json
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents", "--mcp"]
    }
  }
}
```

અથવા જો `rea` ગ્લોબલી ઇન્સ્ટોલ હોય તો:
```json
{
  "mcpServers": {
    "rea": {
      "command": "rea",
      "args": ["--mcp"]
    }
  }
}
```

---

## ભાગ ૨: Tally Prime નું રિવર્સ એન્જિનિયરિંગ કઈ રીતે થાય છે?

Tally Prime ના કોર આર્કિટેક્ચરમાં ૩ મુખ્ય ઘટકો છે:
1. **ડેટા મોડલ (Double-entry Ledger Engine):** જ્યાં દરેક ટ્રાન્ઝેક્શન ક્રેડિટ અને ડેબિટના સમાન ટોટલ સાથે સચવાય છે.
2. **TDL (Tally Definition Language) / UI નેવિગેશન:** કીબોર્ડ-ફર્સ્ટ નેવિગેશન (Hotkeys, Gateway of Tally).
3. **XML/ODBC ઇન્ટિગ્રેશન અને એક્સપોર્ટ:** ડેટા ઇમ્પોર્ટ અને એક્સપોર્ટ કરવા માટેની XML સ્કિમા.

જો તમારી પાસે Tally Prime નું ઇન્સ્ટોલેશન ફોલ્ડર હોય અથવા તેના એક્સપોર્ટ કરેલા XML ડેટા / SQLite બેકઅપ હોય, તો તમે REA CLI ના આ કમાન્ડ્સ વાપરી શકો છો:
- ડેટાબેઝ અથવા ડેટા ફાઇલો જોવા: `rea inspect-sqlite-database` અથવા `rea inspect-pe-resources`
- સ્ટ્રક્ચર અને નેટવર્ક XML તપાસવા: `rea trace` અથવા `rea search`

---

## ભાગ ૩: Tally Prime જેવા ફીચર્સનો તબક્કાવાર રોડમેપ (Step-by-Step Feature Roadmap)

તમારી એપ બનાવવા માટે તમારે VS Code ને નીચે મુજબના એક-એક ફીચર ક્રમબદ્ધ આપવા પડશે:

### તબક્કો ૧: કંપની અને માસ્ટર્સ મેનેજમેન્ટ (Company Creation & Masters)
- **ફીચર વિગત:**
  - Company Creation (નામ, નાણાકીય વર્ષ - FY, ચલણ - Currency, સરનામું).
  - Group Management (Primary Groups: Assets, Liabilities, Incomes, Expenses).
  - Ledger Master (સનડ્રી ડેટર્સ, સનડ્રી ક્રેડિટર્સ, બેંક, કેશ, સેલ્સ, પર્ચેઝ એકાઉન્ટ).
- **ડેટાબેઝ સ્કિમા:** Companies, Groups, Ledgers, Currencies.

### તબક્કો ૨: વાઉચર એન્ટ્રી અને ડબલ-એન્ટ્રી એન્જિન (Voucher Entry & Accounting Engine)
- **ફીચર વિગત:**
  - વાઉચર પ્રકારો: Sales (F8), Purchase (F9), Payment (F5), Receipt (F6), Contra (F4), Journal (F7).
  - ડબલ એન્ટ્રી વેલિડેશન: $\sum Debit = \sum Credit$.
  - એકાઉન્ટિંગ વાઉચર્સનું કીબોર્ડ શોર્ટકટ સાથેનું UI (Enter દબાવવાથી આગલા ફિલ્ડ પર જવું).
- **ડેટાબેઝ સ્કિમા:** Vouchers, VoucherEntries (LedgerID, Amount, Type Debit/Credit).

### તબક્કો ૩: ડે-બુક અને ખાતાવહી (Daybook & Ledger Statements)
- **ફીચર વિગત:**
  - Daybook: તારીખ પ્રમાણે થયેલા તમામ વાઉચર્સની યાદી.
  - Ledger Statement: કોઈ ચોક્કસ ખાતાની વિગત (ઓપનિંગ બેલેન્સ, રનિંગ બેલેન્સ, ક્લોઝિંગ બેલેન્સ).
  - ડ્રિલ-ડાઉન (Drill-down): ડેબુક કે લેજરમાં એન્ટ્રી પર ક્લિક કરતા સીધું વાઉચર એડિટ મોડમાં ખૂલે.

### તબક્કો ૪: નાણાકીય અહેવાલો (Financial Reports)
- **ફીચર વિગત:**
  - Trial Balance (કાચું સરવૈયું): તમામ ખાતાઓનું ડેબિટ-ક્રેડિટ બેલેન્સ.
  - Profit & Loss Statement (નફા-નુકસાન ખાતું): ગ્રોસ પ્રોફિટ અને નેટ પ્રોફિટ ગણતરી.
  - Balance Sheet (પાકું સરવૈયું): Assets = Liabilities.

### તબક્કો ૫: સ્ટોક અને ઇન્વેન્ટરી મેનેજમેન્ટ (Inventory Management)
- **ફીચર વિગત:**
  - Stock Groups, Stock Categories અને Units of Measure (Pcs, Box, Kg).
  - Stock Items (ઓપનિંગ સ્ટોક, સ્ટાન્ડર્ડ રેટ, GST રેટ).
  - ઇન્વેન્ટરી સાથેનું વાઉચર (Sales / Purchase Voucher with Item Details, Quantity, Rate, Amount).
  - Stock Summary રિપોર્ટ.

### તબક્કો ૬: GST અને ટેક્સ ગણતરી (GST & Taxation)
- **ફીચર વિગત:**
  - HSN/SAC કોડ્સ સપોર્ટ.
  - CGST, SGST (રાજ્યની અંદરનું વેચાણ) અને IGST (આંતરરાજ્ય વેચાણ) ની આપોઆપ ગણતરી.
  - GSTR-1, GSTR-3B માટે જરૂરી સેલ્સ/પર્ચેઝ સમરી.

### તબક્કો ૭: ડેટા ઇમ્પોર્ટ/એક્સપોર્ટ (Export & Reporting)
- **ફીચર વિગત:**
  - PDF અને Excel/CSV માં ઇન્વોઇસ અને રિપોર્ટ્સ એક્સપોર્ટ કરવા.
  - Tally-compatible XML Import/Export.

---

## ભાગ ૪: VS Code ને પૂછવા માટેના રેડીમેડ પ્રોમ્પ્ટ્સ (Ready-to-Use Prompts)

તમે VS Code માં Claude Dev / Roo Code / Cursor ને નીચે મુજબના પ્રોમ્પ્ટ્સ એક પછી એક આપીને કોડિંગ કરાવી શકો છો:

#### પ્રોમ્પ્ટ ૧ (પ્રોજેક્ટ સેટઅપ અને કંપની/માસ્ટર્સ મોડેલ):
> "હું Tally Prime જેવી એકાઉન્ટિંગ એપ્લિકેશન બનાવી રહ્યો છું. REA ના આર્કિટેક્ચર સિદ્ધાંતો મુજબ પહેલો તબક્કો શરૂ કરો:
> ૧. Next.js/React (અથવા Electron) + TypeScript + SQLite/PostgreSQL સાથે પ્રોજેક્ટ સ્ટ્રક્ચર સેટઅપ કરો.
> ૨. Company, Group (Assets, Liabilities, Income, Expenses) અને Ledger Master નો ડેટાબેઝ સ્કિમા બનાવો.
> ૩. કંપની બનાવવાનું અને લેજર્સ એડ/મેનેજ કરવાનું UI અને API બનાવો."

#### પ્રોમ્પ્ટ ૨ (ડબલ-એન્ટ્રી વાઉચર એન્જિન):
> "હવે તબક્કો ૨ અમલમાં મૂકો: Tally Prime નું મુખ્ય ડબલ-એન્ટ્રી વાઉચર એન્જિન.
> ૧. Vouchers અને VoucherEntries નો સ્કિમા બનાવો જ્યાં Debit અને Credit નો સરવાળો હંમેશા સમાન રહે.
> ૨. Sales (F8), Purchase (F9), Payment (F5), Receipt (F6), Contra (F4) વાઉચર્સ માટે કીબોર્ડ-ફ્રેન્ડલી એન્ટ્રી ફોર્મ બનાવો.
> ૩. દરેક એન્ટ્રી સેવ થતાં પહેલાં ટ્રાન્ઝેક્શનલ વેલિડેશન ચેક કરો."

#### પ્રોમ્પ્ટ ૩ (ડે-બુક અને ખાતાવહી સ્ટેટમેન્ટ):
> "હવે તબક્કો ૩ અમલમાં મૂકો:
> ૧. Daybook પેજ બનાવો જે તારીખ મુજબના તમામ વાઉચર્સ બતાવે.
> ૨. Ledger Statement પેજ બનાવો જે સિલેક્ટ કરેલા એકાઉન્ટનું ઓપનિંગ બેલેન્સ, ટ્રાન્ઝેક્શન અને ક્લોઝિંગ બેલેન્સ બતાવે.
> ૩. કોઈપણ વાઉચર રો પર Enter દબાવતા ડ્રિલ-ડાઉન થઈને વાઉચર ડિટેલ ખૂલે તેવું ફીચર ઉમેરો."

#### પ્રોમ્પ્ટ ૪ (ટ્રાયલ બેલેન્સ, P&L અને બેલેન્સ શીટ):
> "હવે તબક્કો ૪ અમલમાં મૂકો: Tally Prime જેવા ફાઇનાન્સિયલ રિપોર્ટ્સ.
> ૧. Trial Balance જનરેટ કરો જે તમામ ગ્રુપ્સનું ડેબિટ અને ક્રેડિટ ટોટલ ટેલી કરે.
> ૨. Profit & Loss Statement (ટ્રેડિંગ એકાઉન્ટ અને ગ્રોસ/નેટ પ્રોફિટ સાથે) બનાવો.
> ૩. Balance Sheet (લાયબિલિટીઝ અને એસેટ્સ) રીઅલ-ટાઇમમાં કેલ્ક્યુલેટ કરીને દર્શાવો."

#### પ્રોમ્પ્ટ ૫ (ઇન્વેન્ટરી અને GST):
> "હવે તબક્કો ૫ અને ૬ અમલમાં મૂકો:
> ૧. Stock Items, Units (Pcs, Kg), HSN Code, GST Tax Rates (5%, 12%, 18%, 28%) ઉમેરો.
> ૨. વાઉચરમાં આઇટમ્સ સિલેક્ટ કરતી વખતે આપોઆપ CGST/SGST અથવા IGST કેલ્ક્યુલેટ થઈને ટેક્સ ઇન્વોઇસ બને તેવી સિસ્ટમ બનાવો."
