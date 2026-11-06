import React, { useState } from 'react';
import { Company, LedgerMaster } from '../types/accounting.ts';
import { STANDARD_TALLY_GROUPS } from '../engine/accounting.ts';
import { X } from 'lucide-react';

interface CreateLedgerProps {
  company: Company;
  onSave: (ledger: LedgerMaster) => void;
  onCancel: () => void;
}

export const CreateLedger: React.FC<CreateLedgerProps> = ({
  company,
  onSave,
  onCancel
}) => {
  const [name, setName] = useState('');
  const [groupId, setGroupId] = useState('sundry-debtors');
  const [openingBalance, setOpeningBalance] = useState<number>(0);
  const [balanceType, setBalanceType] = useState<'Dr' | 'Cr'>('Dr');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      alert('Ledger name is required');
      return;
    }

    const newLedger: LedgerMaster = {
      id: `led-${Date.now()}`,
      companyId: company.id,
      name: name.trim(),
      groupId,
      openingBalance: Number(openingBalance) || 0,
      openingBalanceType: balanceType
    };

    onSave(newLedger);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden font-sans">
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <span>Ledger Creation - {company.name}</span>
        <button onClick={onCancel} className="text-gray-700 hover:text-black font-bold p-0.5">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 flex justify-center items-start pt-6 overflow-y-auto px-4">
        <form
          onSubmit={handleSubmit}
          className="w-[580px] bg-white border border-[#1b569e] shadow-xl p-6 flex flex-col text-xs text-gray-800"
        >
          <div className="border-b border-[#1b569e] pb-2 mb-4">
            <h2 className="text-sm font-bold text-[#1b569e]">Ledger Creation</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-medium mb-1">Name *</label>
              <input
                type="text"
                required
                autoFocus
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. ICICI Bank, Office Rent, Shree Ji Furnitures"
                className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-medium"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-1">Under (Group) *</label>
              <select
                value={groupId}
                onChange={e => setGroupId(e.target.value)}
                className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-medium bg-white"
              >
                {STANDARD_TALLY_GROUPS.map(g => (
                  <option key={g.id} value={g.id}>
                    {g.name} ({g.type})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 font-medium mb-1">Opening Balance (₹)</label>
                <input
                  type="number"
                  step="any"
                  value={openingBalance || ''}
                  onChange={e => setOpeningBalance(parseFloat(e.target.value) || 0)}
                  placeholder="0.00"
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-bold"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">Dr / Cr</label>
                <select
                  value={balanceType}
                  onChange={e => setBalanceType(e.target.value as 'Dr' | 'Cr')}
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-bold bg-white"
                >
                  <option value="Dr">Dr</option>
                  <option value="Cr">Cr</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold"
            >
              Cancel (Esc)
            </button>
            <button
              type="submit"
              className="px-5 py-1.5 bg-[#f7b928] hover:bg-[#fab529] text-gray-950 rounded font-bold shadow"
            >
              Accept (Enter)
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
