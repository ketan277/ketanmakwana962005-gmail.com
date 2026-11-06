import {
  AccountingGroup,
  LedgerMaster,
  Voucher,
  TrialBalanceItem,
  ProfitAndLossReport,
  BalanceSheetReport,
  GroupType
} from '../types/accounting.ts';

export const STANDARD_TALLY_GROUPS: AccountingGroup[] = [
  // Primary Groups
  { id: 'branch-divisions', name: 'Branch / Divisions', type: 'Liability', isPrimary: true },
  { id: 'capital-account', name: 'Capital Account', type: 'Liability', isPrimary: true },
  { id: 'current-assets', name: 'Current Assets', type: 'Asset', isPrimary: true },
  { id: 'current-liabilities', name: 'Current Liabilities', type: 'Liability', isPrimary: true },
  { id: 'direct-expenses', name: 'Direct Expenses', type: 'Expense', isPrimary: true },
  { id: 'direct-incomes', name: 'Direct Incomes', type: 'Income', isPrimary: true },
  { id: 'fixed-assets', name: 'Fixed Assets', type: 'Asset', isPrimary: true },
  { id: 'indirect-expenses', name: 'Indirect Expenses', type: 'Expense', isPrimary: true },
  { id: 'indirect-incomes', name: 'Indirect Incomes', type: 'Income', isPrimary: true },
  { id: 'investments', name: 'Investments', type: 'Asset', isPrimary: true },
  { id: 'loans-liability', name: 'Loans (Liability)', type: 'Liability', isPrimary: true },
  { id: 'misc-expenses', name: 'Misc. Expenses (ASSET)', type: 'Asset', isPrimary: true },
  { id: 'purchase-accounts', name: 'Purchase Accounts', type: 'Expense', isPrimary: true },
  { id: 'sales-accounts', name: 'Sales Accounts', type: 'Income', isPrimary: true },
  { id: 'suspense-account', name: 'Suspense A/c', type: 'Liability', isPrimary: true },

  // Sub Groups
  { id: 'bank-accounts', name: 'Bank Accounts', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'bank-od-accounts', name: 'Bank OCC/OD A/c', parentGroup: 'loans-liability', type: 'Liability', isPrimary: false },
  { id: 'cash-in-hand', name: 'Cash-in-Hand', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'deposits-asset', name: 'Deposits (Asset)', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'duties-and-taxes', name: 'Duties & Taxes', parentGroup: 'current-liabilities', type: 'Liability', isPrimary: false },
  { id: 'loans-advances-asset', name: 'Loans & Advances (Asset)', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'provisions', name: 'Provisions', parentGroup: 'current-liabilities', type: 'Liability', isPrimary: false },
  { id: 'reserves-surplus', name: 'Reserves & Surplus', parentGroup: 'capital-account', type: 'Liability', isPrimary: false },
  { id: 'secured-loans', name: 'Secured Loans', parentGroup: 'loans-liability', type: 'Liability', isPrimary: false },
  { id: 'stock-in-hand', name: 'Stock-in-Hand', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'sundry-creditors', name: 'Sundry Creditors', parentGroup: 'current-liabilities', type: 'Liability', isPrimary: false },
  { id: 'sundry-debtors', name: 'Sundry Debtors', parentGroup: 'current-assets', type: 'Asset', isPrimary: false },
  { id: 'unsecured-loans', name: 'Unsecured Loans', parentGroup: 'loans-liability', type: 'Liability', isPrimary: false }
];

export function validateDoubleEntry(entries: { type: 'Dr' | 'Cr'; amount: number }[]): {
  isValid: boolean;
  totalDebit: number;
  totalCredit: number;
  difference: number;
} {
  const totalDebit = entries
    .filter(e => e.type === 'Dr')
    .reduce((sum, e) => sum + (Number(e.amount) || 0), 0);
  const totalCredit = entries
    .filter(e => e.type === 'Cr')
    .reduce((sum, e) => sum + (Number(e.amount) || 0), 0);

  const roundedDr = Math.round(totalDebit * 100) / 100;
  const roundedCr = Math.round(totalCredit * 100) / 100;
  const difference = Math.round(Math.abs(roundedDr - roundedCr) * 100) / 100;

  return {
    isValid: difference === 0 && roundedDr > 0,
    totalDebit: roundedDr,
    totalCredit: roundedCr,
    difference
  };
}

export function calculateLedgerBalances(
  ledgers: LedgerMaster[],
  vouchers: Voucher[]
): Map<string, { balance: number; type: 'Dr' | 'Cr'; totalDebit: number; totalCredit: number }> {
  const result = new Map<string, { balance: number; type: 'Dr' | 'Cr'; totalDebit: number; totalCredit: number }>();

  for (const ledger of ledgers) {
    let debitSum = ledger.openingBalanceType === 'Dr' ? ledger.openingBalance : 0;
    let creditSum = ledger.openingBalanceType === 'Cr' ? ledger.openingBalance : 0;

    for (const voucher of vouchers) {
      for (const entry of voucher.entries) {
        if (entry.ledgerId === ledger.id) {
          if (entry.type === 'Dr') {
            debitSum += entry.amount;
          } else {
            creditSum += entry.amount;
          }
        }
      }
    }

    if (debitSum >= creditSum) {
      result.set(ledger.id, {
        balance: Math.round((debitSum - creditSum) * 100) / 100,
        type: 'Dr',
        totalDebit: Math.round(debitSum * 100) / 100,
        totalCredit: Math.round(creditSum * 100) / 100
      });
    } else {
      result.set(ledger.id, {
        balance: Math.round((creditSum - debitSum) * 100) / 100,
        type: 'Cr',
        totalDebit: Math.round(debitSum * 100) / 100,
        totalCredit: Math.round(creditSum * 100) / 100
      });
    }
  }

  return result;
}

export function generateTrialBalance(
  ledgers: LedgerMaster[],
  vouchers: Voucher[],
  groups: AccountingGroup[] = STANDARD_TALLY_GROUPS
): { items: TrialBalanceItem[]; totalDebit: number; totalCredit: number; isBalanced: boolean } {
  const balances = calculateLedgerBalances(ledgers, vouchers);
  const items: TrialBalanceItem[] = [];

  let totalDebit = 0;
  let totalCredit = 0;

  for (const ledger of ledgers) {
    const bal = balances.get(ledger.id);
    if (!bal || (bal.totalDebit === 0 && bal.totalCredit === 0 && bal.balance === 0)) {
      continue;
    }

    const group = groups.find(g => g.id === ledger.groupId);
    const groupName = group ? group.name : 'Primary';
    const groupType: GroupType = group ? group.type : 'Asset';

    const debit = bal.type === 'Dr' ? bal.balance : 0;
    const credit = bal.type === 'Cr' ? bal.balance : 0;

    totalDebit += debit;
    totalCredit += credit;

    items.push({
      ledgerId: ledger.id,
      ledgerName: ledger.name,
      groupName,
      groupType,
      debit,
      credit
    });
  }

  const roundedDr = Math.round(totalDebit * 100) / 100;
  const roundedCr = Math.round(totalCredit * 100) / 100;

  return {
    items,
    totalDebit: roundedDr,
    totalCredit: roundedCr,
    isBalanced: Math.abs(roundedDr - roundedCr) < 0.01
  };
}

export function generateProfitAndLoss(
  ledgers: LedgerMaster[],
  vouchers: Voucher[],
  groups: AccountingGroup[] = STANDARD_TALLY_GROUPS
): ProfitAndLossReport {
  const balances = calculateLedgerBalances(ledgers, vouchers);

  const tradingIncome: { ledgerName: string; amount: number }[] = [];
  const tradingExpenses: { ledgerName: string; amount: number }[] = [];
  const indirectIncome: { ledgerName: string; amount: number }[] = [];
  const indirectExpenses: { ledgerName: string; amount: number }[] = [];

  for (const ledger of ledgers) {
    const bal = balances.get(ledger.id);
    if (!bal || bal.balance === 0) continue;

    const group = groups.find(g => g.id === ledger.groupId);
    if (!group) continue;

    if (group.id === 'sales-accounts' || group.id === 'direct-incomes') {
      tradingIncome.push({ ledgerName: ledger.name, amount: bal.balance });
    } else if (group.id === 'purchase-accounts' || group.id === 'direct-expenses') {
      tradingExpenses.push({ ledgerName: ledger.name, amount: bal.balance });
    } else if (group.id === 'indirect-incomes') {
      indirectIncome.push({ ledgerName: ledger.name, amount: bal.balance });
    } else if (group.id === 'indirect-expenses') {
      indirectExpenses.push({ ledgerName: ledger.name, amount: bal.balance });
    }
  }

  const totalTradingIncome = tradingIncome.reduce((acc, i) => acc + i.amount, 0);
  const totalTradingExpenses = tradingExpenses.reduce((acc, i) => acc + i.amount, 0);
  const grossProfit = totalTradingIncome - totalTradingExpenses;

  const totalIndirectIncome = indirectIncome.reduce((acc, i) => acc + i.amount, 0);
  const totalIndirectExpenses = indirectExpenses.reduce((acc, i) => acc + i.amount, 0);
  const netProfit = grossProfit + totalIndirectIncome - totalIndirectExpenses;

  return {
    tradingIncome,
    tradingExpenses,
    grossProfit: Math.round(grossProfit * 100) / 100,
    indirectIncome,
    indirectExpenses,
    netProfit: Math.round(netProfit * 100) / 100
  };
}

export function generateBalanceSheet(
  ledgers: LedgerMaster[],
  vouchers: Voucher[],
  groups: AccountingGroup[] = STANDARD_TALLY_GROUPS
): BalanceSheetReport {
  const balances = calculateLedgerBalances(ledgers, vouchers);
  const pnl = generateProfitAndLoss(ledgers, vouchers, groups);

  const liabilitiesMap = new Map<string, { groupName: string; amount: number; ledgers: { name: string; amount: number }[] }>();
  const assetsMap = new Map<string, { groupName: string; amount: number; ledgers: { name: string; amount: number }[] }>();

  let totalLiab = 0;
  let totalAsset = 0;

  for (const ledger of ledgers) {
    const bal = balances.get(ledger.id);
    if (!bal || bal.balance === 0) continue;

    const group = groups.find(g => g.id === ledger.groupId);
    if (!group) continue;

    if (group.type === 'Liability') {
      totalLiab += bal.balance;
      const existing = liabilitiesMap.get(group.name) || { groupName: group.name, amount: 0, ledgers: [] };
      existing.amount += bal.balance;
      existing.ledgers.push({ name: ledger.name, amount: bal.balance });
      liabilitiesMap.set(group.name, existing);
    } else if (group.type === 'Asset') {
      totalAsset += bal.balance;
      const existing = assetsMap.get(group.name) || { groupName: group.name, amount: 0, ledgers: [] };
      existing.amount += bal.balance;
      existing.ledgers.push({ name: ledger.name, amount: bal.balance });
      assetsMap.set(group.name, existing);
    }
  }

  // Net Profit is added to Capital/Liabilities
  totalLiab += pnl.netProfit;

  return {
    liabilities: Array.from(liabilitiesMap.values()),
    assets: Array.from(assetsMap.values()),
    totalLiabilities: Math.round(totalLiab * 100) / 100,
    totalAssets: Math.round(totalAsset * 100) / 100,
    profitOrLoss: pnl.netProfit
  };
}
