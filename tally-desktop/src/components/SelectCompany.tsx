import React, { useState, useEffect, useRef } from 'react';
import { Company } from '../types/accounting.ts';
import { X } from 'lucide-react';

interface SelectCompanyProps {
  companies: Company[];
  onSelectCompany: (company: Company) => void;
  onCreateCompany: () => void;
  onClose?: () => void;
}

export const SelectCompany: React.FC<SelectCompanyProps> = ({
  companies,
  onSelectCompany,
  onCreateCompany,
  onClose
}) => {
  // Navigation options: Action menu followed by company list
  const actionItems = [
    { id: 'create', label: 'Create Company', action: onCreateCompany },
    { id: 'remote', label: 'Select Remote Company', action: () => alert('Remote Company login requires Tally.NET ID') },
    { id: 'path', label: 'Specify Path', action: () => alert('Default Path: C:\\Users\\Public\\TallyPrime\\data') },
    { id: 'drive', label: 'Select from Drive', action: () => alert('Select Drive feature') }
  ];

  // Combined list for keyboard index navigation
  const allSelectables = [
    ...actionItems.map(a => ({ type: 'action' as const, id: a.id, label: a.label, execute: a.action })),
    ...companies.map(c => ({
      type: 'company' as const,
      id: c.id,
      label: c.name,
      company: c,
      execute: () => onSelectCompany(c)
    }))
  ];

  const [selectedIndex, setSelectedIndex] = useState(0); // Default to "Create Company" as in image.png
  const [searchFilter, setSearchFilter] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Keyboard navigation for arrow keys and enter
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < allSelectables.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const current = allSelectables[selectedIndex];
        if (current) {
          current.execute();
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        if (onClose) onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, allSelectables, onClose]);

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden relative font-sans">
      {/* Light Blue Sub-Header Strip */}
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <span>Select Company</span>
        <button
          onClick={onClose}
          className="text-gray-700 hover:text-black font-bold p-0.5"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Main Work Area */}
      <div className="flex-1 flex flex-col items-center pt-5 px-4 overflow-y-auto">
        {/* Select Company Search Box with Yellow Tinted Background */}
        <div className="w-[500px] mb-3">
          <div className="text-center text-xs font-bold text-gray-800 mb-1">
            Select Company
          </div>
          <div className="bg-[#fef4cf] border border-[#d2a33a] p-1 shadow-inner">
            <input
              ref={inputRef}
              type="text"
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
              placeholder=""
              className="w-full bg-transparent outline-none text-xs text-gray-900 font-medium px-1"
            />
          </div>
        </div>

        {/* List of Companies Window */}
        <div className="w-[500px] bg-white border border-[#1b569e] shadow-xl flex flex-col min-h-[440px]">
          {/* Window Header */}
          <div className="bg-[#1b569e] text-white text-xs font-bold px-2 py-1 flex items-center">
            List of Companies
          </div>

          {/* Column Header */}
          <div className="bg-[#e4ecf3] border-b border-gray-300 grid grid-cols-12 px-2 py-1 text-[11px] font-semibold text-gray-700">
            <div className="col-span-6">Data Path/Name</div>
            <div className="col-span-3 text-center">Number</div>
            <div className="col-span-3 text-right">Period</div>
          </div>

          {/* Action Items List */}
          <div className="flex flex-col text-xs text-gray-900 border-b border-gray-300">
            {actionItems.map((item, idx) => {
              const isSelected = selectedIndex === idx;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    setSelectedIndex(idx);
                    item.action();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`px-3 py-1 text-right font-medium cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-[#f7b928] text-black font-semibold'
                      : 'hover:bg-[#fffae8]'
                  }`}
                >
                  {item.label}
                </div>
              );
            })}
          </div>

          {/* Path Header */}
          <div className="px-2 py-1.5 text-xs font-bold text-gray-900 border-b border-gray-200 bg-gray-50 flex flex-col">
            <span>C:\Users\Public\TallyPrime\data</span>
            <span className="text-[11px] font-normal text-gray-600 mt-0.5 cursor-pointer hover:underline">
              ◆ Up
            </span>
          </div>

          {/* Existing Companies List */}
          <div className="flex-1 overflow-y-auto">
            {companies.length === 0 ? (
              <div className="p-4 text-center text-xs text-gray-500 italic">
                No company created yet. Click "Create Company" above.
              </div>
            ) : (
              companies
                .filter(c => c.name.toLowerCase().includes(searchFilter.toLowerCase()))
                .map((company, cIdx) => {
                  const globalIdx = actionItems.length + cIdx;
                  const isSelected = selectedIndex === globalIdx;
                  const startYear = new Date(company.financialYearFrom).getFullYear();
                  const endYear = startYear + 1;

                  return (
                    <div
                      key={company.id}
                      onClick={() => {
                        setSelectedIndex(globalIdx);
                        onSelectCompany(company);
                      }}
                      onMouseEnter={() => setSelectedIndex(globalIdx)}
                      className={`grid grid-cols-12 px-2 py-1.5 text-xs cursor-pointer border-b border-gray-100 ${
                        isSelected
                          ? 'bg-[#f7b928] text-black font-semibold'
                          : 'hover:bg-[#fff9e6] text-gray-800'
                      }`}
                    >
                      <div className="col-span-6 font-bold truncate">
                        {company.name}
                      </div>
                      <div className="col-span-3 text-center text-gray-700">
                        {company.number}
                      </div>
                      <div className="col-span-3 text-right text-gray-600 text-[11px]">
                        1-Apr-{startYear} to 31-Mar-{endYear}
                      </div>
                    </div>
                  );
                })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
