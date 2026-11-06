import React, { useState, useEffect } from 'react';
import { Company, LedgerMaster, Voucher } from './types/accounting.ts';
import {
  getStoredCompanies,
  saveCompanies,
  getStoredLedgers,
  saveLedgers,
  getStoredVouchers,
  saveVouchers,
  getActiveCompanyId,
  setActiveCompanyId
} from './storage/db.ts';
import { TopBar } from './components/TopBar.tsx';
import { StatusBar } from './components/StatusBar.tsx';
import { SelectCompany } from './components/SelectCompany.tsx';
import { CreateCompany } from './components/CreateCompany.tsx';
import { Gateway } from './components/Gateway.tsx';
import { VoucherEntry } from './components/VoucherEntry.tsx';
import { ReportView } from './components/Reports.tsx';
import { CreateLedger } from './components/CreateLedger.tsx';

export default function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [activeCompany, setActiveCompany] = useState<Company | null>(null);
  const [ledgers, setLedgers] = useState<LedgerMaster[]>([]);
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [currentView, setCurrentView] = useState<
    'select-company' | 'create-company' | 'gateway' | 'vouchers' | 'daybook' | 'trial-balance' | 'pnl' | 'balance-sheet' | 'create-ledger'
  >('select-company');
  const [statusMessage, setStatusMessage] = useState<string>('Ready');

  useEffect(() => {
    const loaded = getStoredCompanies();
    setCompanies(loaded);
    const activeId = getActiveCompanyId();
    if (activeId) {
      const found = loaded.find(c => c.id === activeId);
      if (found) {
        setActiveCompany(found);
        setLedgers(getStoredLedgers(found.id));
        setVouchers(getStoredVouchers(found.id));
      }
    }
  }, []);

  const handleSelectCompany = (company: Company) => {
    setActiveCompany(company);
    setActiveCompanyId(company.id);
    setLedgers(getStoredLedgers(company.id));
    setVouchers(getStoredVouchers(company.id));
    setCurrentView('gateway');
    setStatusMessage(`Gateway of Tally: ${company.name}`);
  };

  const handleCreateCompany = (newCompany: Company) => {
    const updated = [...companies, newCompany];
    setCompanies(updated);
    saveCompanies(updated);
    handleSelectCompany(newCompany);
  };

  const handleSaveVoucher = (newVoucher: Voucher) => {
    if (!activeCompany) return;
    const updated = [newVoucher, ...vouchers];
    setVouchers(updated);
    saveVouchers(updated);
    setCurrentView('daybook');
    setStatusMessage(`Voucher #${newVoucher.voucherNumber} (${newVoucher.voucherType}) recorded successfully.`);
  };

  const handleSaveLedger = (newLedger: LedgerMaster) => {
    if (!activeCompany) return;
    const updated = [...ledgers, newLedger];
    setLedgers(updated);
    saveLedgers(updated);
    setCurrentView('gateway');
    setStatusMessage(`Ledger ${newLedger.name} created.`);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#9cb3be] overflow-hidden select-none">
      {/* Top Bar matching image.png */}
      <TopBar
        onCompanyClick={() => setCurrentView('select-company')}
        onGoToClick={() => setCurrentView('gateway')}
        onHelpClick={() => alert('Tally Prime Shortcuts: F4-Contra, F5-Payment, F6-Receipt, F7-Journal, F8-Sales, F9-Purchase. Esc to go back.')}
      />

      {/* Main Container View Switcher */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {currentView === 'select-company' && (
          <SelectCompany
            companies={companies}
            onSelectCompany={handleSelectCompany}
            onCreateCompany={() => setCurrentView('create-company')}
            onClose={() => activeCompany && setCurrentView('gateway')}
          />
        )}

        {currentView === 'create-company' && (
          <CreateCompany
            onSave={handleCreateCompany}
            onCancel={() => setCurrentView(activeCompany ? 'gateway' : 'select-company')}
            existingCount={companies.length}
          />
        )}

        {currentView === 'gateway' && activeCompany && (
          <Gateway
            company={activeCompany}
            onNavigate={view => setCurrentView(view)}
          />
        )}

        {currentView === 'vouchers' && activeCompany && (
          <VoucherEntry
            company={activeCompany}
            ledgers={ledgers}
            onSaveVoucher={handleSaveVoucher}
            onCancel={() => setCurrentView('gateway')}
            nextVoucherNumber={vouchers.length + 1}
          />
        )}

        {currentView === 'create-ledger' && activeCompany && (
          <CreateLedger
            company={activeCompany}
            onSave={handleSaveLedger}
            onCancel={() => setCurrentView('gateway')}
          />
        )}

        {(currentView === 'daybook' ||
          currentView === 'trial-balance' ||
          currentView === 'pnl' ||
          currentView === 'balance-sheet') &&
          activeCompany && (
            <ReportView
              type={currentView}
              company={activeCompany}
              ledgers={ledgers}
              vouchers={vouchers}
              onBack={() => setCurrentView('gateway')}
            />
          )}
      </main>

      {/* Bottom Status Bar matching image.png */}
      <StatusBar
        onQuit={() => {
          if (confirm('Do you want to quit Tally Prime?')) {
            window.close();
          }
        }}
        message={statusMessage}
      />
    </div>
  );
}
