import { describe, it, expect } from 'vitest';
import {
  STANDARD_TALLY_GROUPS,
  validateDoubleEntry,
  calculateLedgerBalances,
  generateTrialBalance,
  generateProfitAndLoss,
  generateBalanceSheet
} from '../accounting.ts';
import { LedgerMaster, Voucher } from '../../types/accounting.ts';

describe('Accounting Engine', () => {
  it('should validate 28 standard Tally groups', () => {
    expect(STANDARD_TALLY_GROUPS.length).toBe(28);
    const capital = STANDARD_TALLY_GROUPS.find(g => g.id === 'capital-account');
    expect(capital?.type).toBe('Liability');
    const cash = STANDARD_TALLY_GROUPS.find(g => g.id === 'cash-in-hand');
    expect(cash?.type).toBe('Asset');
  });

  it('should validate double-entry balance correctly', () => {
    const validEntries = [
      { type: 'Dr' as const, amount: 5000 },
      { type: 'Cr' as const, amount: 5000 }
    ];
    const validation = validateDoubleEntry(validEntries);
    expect(validation.isValid).toBe(true);
    expect(validation.totalDebit).toBe(5000);
    expect(validation.totalCredit).toBe(5000);
    expect(validation.difference).toBe(0);

    const invalidEntries = [
      { type: 'Dr' as const, amount: 5000 },
      { type: 'Cr' as const, amount: 4500 }
    ];
    const invalidValidation = validateDoubleEntry(invalidEntries);
    expect(invalidValidation.isValid).toBe(false);
    expect(invalidValidation.difference).toBe(500);
  });

  it('should compute ledger balances and trial balance accurately', () => {
    const ledgers: LedgerMaster[] = [
      {
        id: 'led-capital',
        companyId: 'comp-1',
        name: 'Capital Account',
        groupId: 'capital-account',
        openingBalance: 100000,
        openingBalanceType: 'Cr'
      },
      {
        id: 'led-bank',
        companyId: 'comp-1',
        name: 'HDFC Bank',
        groupId: 'bank-accounts',
        openingBalance: 100000,
        openingBalanceType: 'Dr'
      },
      {
        id: 'led-sales',
        companyId: 'comp-1',
        name: 'Sales Account',
        groupId: 'sales-accounts',
        openingBalance: 0,
        openingBalanceType: 'Cr'
      },
      {
        id: 'led-debtor',
        companyId: 'comp-1',
        name: 'ABC Corp',
        groupId: 'sundry-debtors',
        openingBalance: 0,
        openingBalanceType: 'Dr'
      }
    ];

    const vouchers: Voucher[] = [
      {
        id: 'v-1',
        companyId: 'comp-1',
        voucherNumber: 1,
        voucherType: 'Sales',
        date: '2026-04-01',
        totalAmount: 25000,
        createdAt: '2026-04-01T10:00:00Z',
        entries: [
          { id: 'e1', ledgerId: 'led-debtor', ledgerName: 'ABC Corp', type: 'Dr', amount: 25000 },
          { id: 'e2', ledgerId: 'led-sales', ledgerName: 'Sales Account', type: 'Cr', amount: 25000 }
        ]
      }
    ];

    const balances = calculateLedgerBalances(ledgers, vouchers);
    expect(balances.get('led-debtor')?.balance).toBe(25000);
    expect(balances.get('led-debtor')?.type).toBe('Dr');
    expect(balances.get('led-sales')?.balance).toBe(25000);
    expect(balances.get('led-sales')?.type).toBe('Cr');

    const tb = generateTrialBalance(ledgers, vouchers);
    expect(tb.isBalanced).toBe(true);
    expect(tb.totalDebit).toBe(125000);
    expect(tb.totalCredit).toBe(125000);

    const pnl = generateProfitAndLoss(ledgers, vouchers);
    expect(pnl.grossProfit).toBe(25000);
    expect(pnl.netProfit).toBe(25000);

    const bs = generateBalanceSheet(ledgers, vouchers);
    expect(bs.totalAssets).toBe(125000); // Bank 100k + Debtor 25k
    expect(bs.totalLiabilities).toBe(125000); // Capital 100k + Profit 25k
  });
});
