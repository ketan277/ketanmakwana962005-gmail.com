import React, { useState } from 'react';
import { Company } from '../types/accounting.ts';
import { X } from 'lucide-react';

interface CreateCompanyProps {
  onSave: (company: Company) => void;
  onCancel: () => void;
  existingCount: number;
}

export const CreateCompany: React.FC<CreateCompanyProps> = ({
  onSave,
  onCancel,
  existingCount
}) => {
  const nextCompanyNumber = (10000 + existingCount).toString();

  const [formData, setFormData] = useState({
    name: '',
    mailingName: '',
    address: '',
    state: 'Gujarat',
    country: 'India',
    pincode: '380001',
    financialYearFrom: '2026-04-01',
    booksBeginningFrom: '2026-04-01',
    currencySymbol: '₹',
    formalName: 'INR'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Company Name is required');
      return;
    }

    const newCompany: Company = {
      id: `comp-${Date.now()}`,
      number: nextCompanyNumber,
      name: formData.name.trim(),
      mailingName: formData.mailingName || formData.name.trim(),
      address: formData.address,
      state: formData.state,
      country: formData.country,
      pincode: formData.pincode,
      financialYearFrom: formData.financialYearFrom,
      booksBeginningFrom: formData.booksBeginningFrom,
      currencySymbol: formData.currencySymbol,
      formalName: formData.formalName,
      createdAt: new Date().toISOString(),
      dataDirectory: 'C:\\Users\\Public\\TallyPrime\\data'
    };

    onSave(newCompany);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden relative font-sans">
      {/* Sub Header */}
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <span>Company Creation</span>
        <button
          onClick={onCancel}
          className="text-gray-700 hover:text-black font-bold p-0.5"
          title="Cancel (Esc)"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Main Creation Form styled after Tally Prime */}
      <div className="flex-1 flex justify-center items-start pt-6 overflow-y-auto px-4">
        <form
          onSubmit={handleSubmit}
          className="w-[720px] bg-white border border-[#1b569e] shadow-xl p-6 flex flex-col text-xs text-gray-800"
        >
          {/* Header */}
          <div className="border-b border-[#1b569e] pb-2 mb-4 flex justify-between items-center">
            <h2 className="text-sm font-bold text-[#1b569e]">Company Creation</h2>
            <span className="text-gray-500 font-mono text-[11px]">Number: {nextCompanyNumber}</span>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Left Column: Basic Details */}
            <div className="space-y-3">
              <h3 className="font-bold text-gray-900 border-b border-gray-200 pb-1">
                Company Details
              </h3>

              <div>
                <label className="block text-gray-700 font-medium mb-1">Company Name *</label>
                <input
                  type="text"
                  required
                  autoFocus
                  value={formData.name}
                  onChange={e => {
                    const name = e.target.value;
                    setFormData(prev => ({
                      ...prev,
                      name,
                      mailingName: prev.mailingName === prev.name ? name : prev.mailingName
                    }));
                  }}
                  placeholder="e.g. Acme Industries Ltd"
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-medium"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">Mailing Name</label>
                <input
                  type="text"
                  value={formData.mailingName}
                  onChange={e => setFormData({ ...formData, mailingName: e.target.value })}
                  placeholder="Mailing name"
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">Address</label>
                <textarea
                  rows={3}
                  value={formData.address}
                  onChange={e => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Street, locality, office..."
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-gray-700 font-medium mb-1">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={e => setFormData({ ...formData, state: e.target.value })}
                    className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 font-medium mb-1">Pincode</label>
                  <input
                    type="text"
                    value={formData.pincode}
                    onChange={e => setFormData({ ...formData, pincode: e.target.value })}
                    className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                  />
                </div>
              </div>
            </div>

            {/* Right Column: Financial Year & Currency */}
            <div className="space-y-3">
              <h3 className="font-bold text-gray-900 border-b border-gray-200 pb-1">
                Financial Year & Currency
              </h3>

              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Financial year beginning from
                </label>
                <input
                  type="date"
                  value={formData.financialYearFrom}
                  onChange={e => setFormData({ ...formData, financialYearFrom: e.target.value })}
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Books beginning from
                </label>
                <input
                  type="date"
                  value={formData.booksBeginningFrom}
                  onChange={e => setFormData({ ...formData, booksBeginningFrom: e.target.value })}
                  className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2">
                <div>
                  <label className="block text-gray-700 font-medium mb-1">
                    Base currency symbol
                  </label>
                  <input
                    type="text"
                    value={formData.currencySymbol}
                    onChange={e => setFormData({ ...formData, currencySymbol: e.target.value })}
                    className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded font-bold"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 font-medium mb-1">Formal name</label>
                  <input
                    type="text"
                    value={formData.formalName}
                    onChange={e => setFormData({ ...formData, formalName: e.target.value })}
                    className="w-full border border-gray-400 p-1.5 focus:bg-[#fef4cf] focus:border-[#d2a33a] outline-none rounded"
                  />
                </div>
              </div>

              <div className="bg-[#f0f5fa] border border-[#d0e0ed] p-3 rounded text-[11px] text-gray-600 mt-4">
                <span className="font-bold text-gray-800">Tally Prime Note:</span>
                <p className="mt-1">
                  Default 28 accounting groups and primary ledgers (Cash & Profit/Loss A/c) will be automatically initialized for this company.
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold transition-colors"
            >
              Cancel (Esc)
            </button>
            <button
              type="submit"
              className="px-5 py-1.5 bg-[#f7b928] hover:bg-[#fab529] text-gray-950 rounded font-bold shadow transition-colors"
            >
              Accept (Enter)
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
