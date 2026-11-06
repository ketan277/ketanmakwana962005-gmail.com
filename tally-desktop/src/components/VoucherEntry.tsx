import React, { useState, useEffect } from 'react';
import { Company, LedgerMaster, Voucher, VoucherType, VoucherEntryItem } from '../types/accounting.ts';
import { validateDoubleEntry } from '../engine/accounting.ts';
import { X, Plus, Trash2 } from 'lucide-react';

interface VoucherEntryProps {
  company: Company;
  ledgers: LedgerMaster[];
  onSaveVoucher: (voucher: Voucher) => void;
  onCancel: () => void;
  nextVoucherNumber: number;
}

export const VoucherEntry: React.FC<VoucherEntryProps> = ({
  company,
  ledgers,
  onSaveVoucher,
  onCancel,
  nextVoucherNumber
}) => {
  const [voucherType, setVoucherType] = useState<VoucherType>('Payment');
  const [date, setDate] = useState('2026-04-02');
  const [narration, setNarration] = useState('');

  const [entries, setEntries] = useState<VoucherEntryItem[]>([
    {
      id: 'entry-1',
      ledgerId: ledgers[0]?.id || '',
      ledgerName: ledgers[0]?.name || '',
      type: 'Dr',
      amount: 1000
    },
    {
      id: 'entry-2',
      ledgerId: ledgers[1]?.id || '',
      ledgerName: ledgers[1]?.name || '',
      type: 'Cr',
      amount: 1000
    }
  ]);

  const validation = validateDoubleEntry(entries);

  // Keyboard shortcut listener for F4 - F9
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F4') {
        e.preventDefault();
        setVoucherType('Contra');
      } else if (e.key === 'F5') {
        e.preventDefault();
        setVoucherType('Payment');
      } else if (e.key === 'F6') {
        e.preventDefault();
        setVoucherType('Receipt');
      } else if (e.key === 'F7') {
        e.preventDefault();
        setVoucherType('Journal');
      } else if (e.key === 'F8') {
        e.preventDefault();
        setVoucherType('Sales');
      } else if (e.key === 'F9') {
        e.preventDefault();
        setVoucherType('Purchase');
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onCancel]);

  const addEntryRow = () => {
    setEntries(prev => [
      ...prev,
      {
        id: `entry-${Date.now()}`,
        ledgerId: ledgers[0]?.id || '',
        ledgerName: ledgers[0]?.name || '',
        type: 'Cr',
        amount: 0
      }
    ]);
  };

  const removeEntryRow = (idx: number) => {
    if (entries.length <= 2) return;
    setEntries(prev => prev.filter((_, i) => i !== idx));
  };

  const updateEntry = (idx: number, updates: Partial<VoucherEntryItem>) => {
    setEntries(prev => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], ...updates };
      if (updates.ledgerId) {
        const found = ledgers.find(l => l.id === updates.ledgerId);
        if (found) copy[idx].ledgerName = found.name;
      }
      return copy;
    });
  };

  const handleSave = () => {
    if (!validation.isValid) {
      alert(`Debit and Credit amounts must match! Difference: ₹${validation.difference}`);
      return;
    }

    const newVoucher: Voucher = {
      id: `v-${Date.now()}`,
      companyId: company.id,
      voucherNumber: nextVoucherNumber,
      voucherType,
      date,
      narration,
      entries,
      totalAmount: validation.totalDebit,
      createdAt: new Date().toISOString()
    };

    onSaveVoucher(newVoucher);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden font-sans">
      {/* Sub Header */}
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <span>Accounting Voucher Creation ({voucherType})</span>
        <button onClick={onCancel} className="text-gray-700 hover:text-black font-bold p-0.5">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 flex flex-col p-3 gap-3 overflow-hidden">
        {/* Top Voucher Bar with Hotkeys */}
        <div className="bg-[#1b569e] text-white p-2 rounded flex items-center justify-between shadow text-xs">
          <div className="flex items-center space-x-4">
            <span className="font-bold text-sm bg-yellow-400 text-black px-2 py-0.5 rounded">
              {voucherType}
            </span>
            <span>No. <b>{nextVoucherNumber}</b></span>
            <span>Company: <b>{company.name}</b></span>
          </div>

          <div className="flex items-center space-x-2">
            {(['Contra', 'Payment', 'Receipt', 'Journal', 'Sales', 'Purchase'] as VoucherType[]).map((type, i) => {
              const hotkey = `F${i + 4}`;
              return (
                <button
                  key={type}
                  onClick={() => setVoucherType(type)}
                  className={`px-2 py-0.5 rounded font-medium text-[11px] border transition-colors ${
                    voucherType === type
                      ? 'bg-yellow-400 text-black border-yellow-500 font-bold'
                      : 'bg-[#2968b5] hover:bg-[#3476c8] border-[#387fd6]'
                  }`}
                >
                  <span className="underline mr-1">{hotkey}</span>
                  {type}
                </button>
              );
            })}
          </div>
        </div>

        {/* Voucher Form Table */}
        <div className="flex-1 bg-white border border-[#1b569e] shadow flex flex-col overflow-hidden text-xs">
          {/* Header Row */}
          <div className="p-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <span className="font-semibold text-gray-700">Date:</span>
              <input
                type="date"
                value={date}
                onChange={e => setDate(e.target.value)}
                className="border border-gray-300 p-1 rounded font-medium"
              />
            </div>
            <div className="text-[11px] text-gray-500">
              * Tally Prime Standard Double-Entry Mode
            </div>
          </div>

          {/* Entries Table */}
          <div className="flex-1 overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#e4ecf3] border-b border-gray-300 text-gray-700 text-[11px]">
                  <th className="p-2 w-16 text-center">Dr / Cr</th>
                  <th className="p-2">Particulars (Ledger)</th>
                  <th className="p-2 w-32 text-right">Debit (₹)</th>
                  <th className="p-2 w-32 text-right">Credit (₹)</th>
                  <th className="p-2 w-12 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {entries.map((entry, idx) => (
                  <tr key={entry.id} className="hover:bg-yellow-50">
                    <td className="p-2 text-center">
                      <select
                        value={entry.type}
                        onChange={e => updateEntry(idx, { type: e.target.value as 'Dr' | 'Cr' })}
                        className="bg-transparent font-bold text-[#105696] outline-none"
                      >
                        <option value="Dr">Dr</option>
                        <option value="Cr">Cr</option>
                      </select>
                    </td>

                    <td className="p-2">
                      <select
                        value={entry.ledgerId}
                        onChange={e => updateEntry(idx, { ledgerId: e.target.value })}
                        className="w-full border border-gray-300 p-1 rounded outline-none font-medium text-xs bg-white focus:border-[#105696]"
                      >
                        {ledgers.map(l => (
                          <option key={l.id} value={l.id}>
                            {l.name}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td className="p-2 text-right">
                      {entry.type === 'Dr' ? (
                        <input
                          type="number"
                          step="any"
                          value={entry.amount || ''}
                          onChange={e => updateEntry(idx, { amount: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-gray-300 p-1 rounded text-right font-bold outline-none focus:bg-[#fef4cf]"
                        />
                      ) : (
                        <span className="text-gray-400 font-mono">-</span>
                      )}
                    </td>

                    <td className="p-2 text-right">
                      {entry.type === 'Cr' ? (
                        <input
                          type="number"
                          step="any"
                          value={entry.amount || ''}
                          onChange={e => updateEntry(idx, { amount: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-gray-300 p-1 rounded text-right font-bold outline-none focus:bg-[#fef4cf]"
                        />
                      ) : (
                        <span className="text-gray-400 font-mono">-</span>
                      )}
                    </td>

                    <td className="p-2 text-center">
                      {entries.length > 2 && (
                        <button
                          onClick={() => removeEntryRow(idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="p-2">
              <button
                onClick={addEntryRow}
                className="flex items-center text-xs text-[#105696] hover:underline font-semibold"
              >
                <Plus className="w-3.5 h-3.5 mr-1" /> Add Entry Row
              </button>
            </div>
          </div>

          {/* Narration and Totals Footer */}
          <div className="bg-[#f7f9fb] border-t border-gray-300 p-3">
            <div className="flex justify-between items-center mb-2">
              <div className="flex-1 mr-6">
                <span className="text-gray-700 font-medium mr-2">Narration:</span>
                <input
                  type="text"
                  value={narration}
                  onChange={e => setNarration(e.target.value)}
                  placeholder="Being amount paid / received..."
                  className="w-3/4 border border-gray-300 p-1 text-xs rounded outline-none focus:bg-[#fef4cf]"
                />
              </div>

              {/* Total Summary */}
              <div className="flex items-center space-x-6 text-xs">
                <div>
                  <span className="text-gray-600 font-medium">Total Debit: </span>
                  <span className="font-bold text-[#105696]">₹{validation.totalDebit.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-gray-600 font-medium">Total Credit: </span>
                  <span className="font-bold text-[#105696]">₹{validation.totalCredit.toLocaleString()}</span>
                </div>
                <div>
                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      validation.isValid
                        ? 'bg-green-100 text-green-800 border border-green-300'
                        : 'bg-red-100 text-red-800 border border-red-300'
                    }`}
                  >
                    {validation.isValid ? 'Balanced ✓' : `Difference: ₹${validation.difference}`}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-2 border-t border-gray-200">
              <button
                onClick={onCancel}
                className="px-4 py-1 bg-gray-200 hover:bg-gray-300 rounded font-semibold text-gray-800"
              >
                Cancel (Esc)
              </button>
              <button
                onClick={handleSave}
                disabled={!validation.isValid}
                className={`px-5 py-1 rounded font-bold shadow transition-colors ${
                  validation.isValid
                    ? 'bg-[#f7b928] hover:bg-[#fab529] text-gray-950 cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Accept (Enter)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
