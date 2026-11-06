import { Company, LedgerMaster, Voucher } from '../types/accounting.ts';

const STORAGE_KEY_COMPANIES = 'tally_companies';
const STORAGE_KEY_LEDGERS = 'tally_ledgers';
const STORAGE_KEY_VOUCHERS = 'tally_vouchers';
const STORAGE_KEY_ACTIVE_COMPANY = 'tally_active_company';

export const INITIAL_COMPANIES: Company[] = [
  {
    id: 'comp-10000',
    number: '10000',
    name: 'Shree Krishna Traders Pvt Ltd',
    mailingName: 'Shree Krishna Traders Pvt Ltd',
    address: 'Ring Road, Surat, Gujarat',
    state: 'Gujarat',
    country: 'India',
    pincode: '395002',
    financialYearFrom: '2026-04-01',
    booksBeginningFrom: '2026-04-01',
    currencySymbol: '₹',
    formalName: 'INR',
    createdAt: '2026-04-01T00:00:00.000Z',
    dataDirectory: 'C:\\Users\\Public\\TallyPrime\\data'
  }
];

export const INITIAL_LEDGERS: LedgerMaster[] = [
  {
    id: 'led-1',
    companyId: 'comp-10000',
    name: 'Capital Account',
    groupId: 'capital-account',
    openingBalance: 500000,
    openingBalanceType: 'Cr'
  },
  {
    id: 'led-2',
    companyId: 'comp-10000',
    name: 'State Bank of India',
    groupId: 'bank-accounts',
    openingBalance: 350000,
    openingBalanceType: 'Dr'
  },
  {
    id: 'led-3',
    companyId: 'comp-10000',
    name: 'Cash',
    groupId: 'cash-in-hand',
    openingBalance: 150000,
    openingBalanceType: 'Dr'
  },
  {
    id: 'led-4',
    companyId: 'comp-10000',
    name: 'Sales Account',
    groupId: 'sales-accounts',
    openingBalance: 0,
    openingBalanceType: 'Cr'
  },
  {
    id: 'led-5',
    companyId: 'comp-10000',
    name: 'Purchase Account',
    groupId: 'purchase-accounts',
    openingBalance: 0,
    openingBalanceType: 'Dr'
  },
  {
    id: 'led-6',
    companyId: 'comp-10000',
    name: 'Radhe Enterprises (Sundry Debtor)',
    groupId: 'sundry-debtors',
    openingBalance: 45000,
    openingBalanceType: 'Dr'
  },
  {
    id: 'led-7',
    companyId: 'comp-10000',
    name: 'Shiv Shakti Supplies (Sundry Creditor)',
    groupId: 'sundry-creditors',
    openingBalance: 30000,
    openingBalanceType: 'Cr'
  },
  {
    id: 'led-8',
    companyId: 'comp-10000',
    name: 'Rent Expenses',
    groupId: 'indirect-expenses',
    openingBalance: 0,
    openingBalanceType: 'Dr'
  }
];

export const INITIAL_VOUCHERS: Voucher[] = [
  {
    id: 'v-101',
    companyId: 'comp-10000',
    voucherNumber: 1,
    voucherType: 'Sales',
    date: '2026-04-02',
    narration: 'Being goods sold on credit to Radhe Enterprises',
    totalAmount: 25000,
    createdAt: '2026-04-02T11:00:00Z',
    entries: [
      { id: 've-1', ledgerId: 'led-6', ledgerName: 'Radhe Enterprises (Sundry Debtor)', type: 'Dr', amount: 25000 },
      { id: 've-2', ledgerId: 'led-4', ledgerName: 'Sales Account', type: 'Cr', amount: 25000 }
    ]
  },
  {
    id: 'v-102',
    companyId: 'comp-10000',
    voucherNumber: 2,
    voucherType: 'Receipt',
    date: '2026-04-05',
    narration: 'Being payment received by bank from Radhe Enterprises',
    totalAmount: 15000,
    createdAt: '2026-04-05T14:30:00Z',
    entries: [
      { id: 've-3', ledgerId: 'led-2', ledgerName: 'State Bank of India', type: 'Dr', amount: 15000 },
      { id: 've-4', ledgerId: 'led-6', ledgerName: 'Radhe Enterprises (Sundry Debtor)', type: 'Cr', amount: 15000 }
    ]
  }
];

export function getStoredCompanies(): Company[] {
  const data = localStorage.getItem(STORAGE_KEY_COMPANIES);
  if (!data) {
    localStorage.setItem(STORAGE_KEY_COMPANIES, JSON.stringify(INITIAL_COMPANIES));
    return INITIAL_COMPANIES;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_COMPANIES;
  }
}

export function saveCompanies(companies: Company[]): void {
  localStorage.setItem(STORAGE_KEY_COMPANIES, JSON.stringify(companies));
}

export function getStoredLedgers(companyId: string): LedgerMaster[] {
  const data = localStorage.getItem(STORAGE_KEY_LEDGERS);
  let allLedgers: LedgerMaster[] = [];
  if (!data) {
    allLedgers = INITIAL_LEDGERS;
    localStorage.setItem(STORAGE_KEY_LEDGERS, JSON.stringify(allLedgers));
  } else {
    try {
      allLedgers = JSON.parse(data);
    } catch {
      allLedgers = INITIAL_LEDGERS;
    }
  }
  return allLedgers.filter(l => l.companyId === companyId);
}

export function saveLedgers(ledgers: LedgerMaster[]): void {
  localStorage.setItem(STORAGE_KEY_LEDGERS, JSON.stringify(ledgers));
}

export function getStoredVouchers(companyId: string): Voucher[] {
  const data = localStorage.getItem(STORAGE_KEY_VOUCHERS);
  let allVouchers: Voucher[] = [];
  if (!data) {
    allVouchers = INITIAL_VOUCHERS;
    localStorage.setItem(STORAGE_KEY_VOUCHERS, JSON.stringify(allVouchers));
  } else {
    try {
      allVouchers = JSON.parse(data);
    } catch {
      allVouchers = INITIAL_VOUCHERS;
    }
  }
  return allVouchers.filter(v => v.companyId === companyId);
}

export function saveVouchers(vouchers: Voucher[]): void {
  localStorage.setItem(STORAGE_KEY_VOUCHERS, JSON.stringify(vouchers));
}

export function getActiveCompanyId(): string | null {
  return localStorage.getItem(STORAGE_KEY_ACTIVE_COMPANY);
}

export function setActiveCompanyId(id: string | null): void {
  if (id) {
    localStorage.setItem(STORAGE_KEY_ACTIVE_COMPANY, id);
  } else {
    localStorage.removeItem(STORAGE_KEY_ACTIVE_COMPANY);
  }
}
