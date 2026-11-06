export type GroupType = 'Asset' | 'Liability' | 'Income' | 'Expense';

export interface AccountingGroup {
  id: string;
  name: string;
  parentGroup?: string;
  type: GroupType;
  isPrimary: boolean;
}

export interface LedgerMaster {
  id: string;
  companyId: string;
  name: string;
  groupId: string;
  openingBalance: number;
  openingBalanceType: 'Dr' | 'Cr';
  currentBalance?: number;
  currentBalanceType?: 'Dr' | 'Cr';
  mailingAddress?: string;
  state?: string;
  country?: string;
  pincode?: string;
  gstin?: string;
}

export type VoucherType =
  | 'Contra'     // F4
  | 'Payment'    // F5
  | 'Receipt'    // F6
  | 'Journal'    // F7
  | 'Sales'      // F8
  | 'Purchase';  // F9

export interface VoucherEntryItem {
  id: string;
  ledgerId: string;
  ledgerName: string;
  type: 'Dr' | 'Cr';
  amount: number;
  particulars?: string;
}

export interface Voucher {
  id: string;
  companyId: string;
  voucherNumber: number;
  voucherType: VoucherType;
  date: string; // YYYY-MM-DD
  referenceNo?: string;
  narration?: string;
  entries: VoucherEntryItem[];
  totalAmount: number;
  createdAt: string;
}

export interface Company {
  id: string;
  number: string; // e.g. "10000"
  name: string;
  mailingName: string;
  address: string;
  state: string;
  country: string;
  pincode: string;
  financialYearFrom: string; // YYYY-MM-DD
  booksBeginningFrom: string; // YYYY-MM-DD
  currencySymbol: string; // "₹"
  formalName: string; // "INR"
  createdAt: string;
  dataDirectory: string;
}

export interface TrialBalanceItem {
  ledgerId: string;
  ledgerName: string;
  groupName: string;
  groupType: GroupType;
  debit: number;
  credit: number;
}

export interface ProfitAndLossReport {
  tradingIncome: { ledgerName: string; amount: number }[];
  tradingExpenses: { ledgerName: string; amount: number }[];
  grossProfit: number;
  indirectIncome: { ledgerName: string; amount: number }[];
  indirectExpenses: { ledgerName: string; amount: number }[];
  netProfit: number;
}

export interface BalanceSheetReport {
  liabilities: { groupName: string; amount: number; ledgers: { name: string; amount: number }[] }[];
  assets: { groupName: string; amount: number; ledgers: { name: string; amount: number }[] }[];
  totalLiabilities: number;
  totalAssets: number;
  profitOrLoss: number;
}
