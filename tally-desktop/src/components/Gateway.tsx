import React, { useState, useEffect } from 'react';
import { Company } from '../types/accounting.ts';

type GatewayView = 'vouchers' | 'daybook' | 'trial-balance' | 'pnl' | 'balance-sheet' | 'select-company' | 'create-ledger';

interface GatewayProps {
  company: Company;
  onNavigate: (view: GatewayView) => void;
}

interface MenuItem {
  label: string;
  key: string;
  hotkey: string;
  view: GatewayView;
}

interface MenuSection {
  category: string;
  items: MenuItem[];
}

export const Gateway: React.FC<GatewayProps> = ({ company, onNavigate }) => {
  const [selectedIdx, setSelectedIdx] = useState(0);

  const menuSections: MenuSection[] = [
    {
      category: 'MASTERS',
      items: [
        { label: 'Create', key: 'C', hotkey: 'c', view: 'create-ledger' },
        { label: 'Alter', key: 'A', hotkey: 'a', view: 'create-ledger' },
        { label: 'Chart of Accounts', key: 'H', hotkey: 'h', view: 'trial-balance' }
      ]
    },
    {
      category: 'TRANSACTIONS',
      items: [
        { label: 'Vouchers', key: 'V', hotkey: 'v', view: 'vouchers' },
        { label: 'Day Book', key: 'K', hotkey: 'k', view: 'daybook' }
      ]
    },
    {
      category: 'UTILITIES',
      items: [
        { label: 'Banking', key: 'N', hotkey: 'n', view: 'daybook' }
      ]
    },
    {
      category: 'REPORTS',
      items: [
        { label: 'Balance Sheet', key: 'B', hotkey: 'b', view: 'balance-sheet' },
        { label: 'Profit & Loss A/c', key: 'P', hotkey: 'p', view: 'pnl' },
        { label: 'Stock Summary', key: 'S', hotkey: 's', view: 'trial-balance' },
        { label: 'Trial Balance', key: 'T', hotkey: 't', view: 'trial-balance' }
      ]
    }
  ];

  const flatItems: MenuItem[] = menuSections.reduce<MenuItem[]>((acc, sec) => acc.concat(sec.items), []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const pressedKey = e.key.toLowerCase();
      // Check direct hotkeys
      const match = flatItems.find(item => item.hotkey === pressedKey);
      if (match) {
        e.preventDefault();
        onNavigate(match.view);
        return;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIdx(prev => (prev < flatItems.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIdx(prev => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const current = flatItems[selectedIdx];
        if (current) onNavigate(current.view);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onNavigate('select-company');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIdx, flatItems, onNavigate]);

  const startYear = new Date(company.financialYearFrom).getFullYear();
  const endYear = startYear + 1;

  let runningItemIndex = 0;

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden font-sans">
      {/* Sub Header */}
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <span>Gateway of Tally</span>
        <button
          onClick={() => onNavigate('select-company')}
          className="text-gray-700 hover:text-black font-medium underline"
        >
          Change Company (F3)
        </button>
      </div>

      {/* Main Dual Pane Content */}
      <div className="flex-1 grid grid-cols-12 p-3 gap-3 overflow-hidden">
        {/* Left Pane: Company Info & Period */}
        <div className="col-span-5 bg-white border border-[#1b569e] shadow flex flex-col text-xs text-gray-800">
          <div className="bg-[#1b569e] text-white font-bold px-3 py-1.5 flex justify-between">
            <span>CURRENT PERIOD</span>
            <span>CURRENT DATE</span>
          </div>

          <div className="flex justify-between px-3 py-1 bg-gray-50 border-b border-gray-200 font-medium">
            <span>1-Apr-{startYear} to 31-Mar-{endYear}</span>
            <span>Thursday, 2-Apr-{startYear}</span>
          </div>

          <div className="p-3 border-b border-gray-200">
            <span className="text-[11px] text-gray-500 font-semibold uppercase tracking-wider block">
              Name of Company
            </span>
            <span className="text-sm font-bold text-[#1b569e] block mt-0.5">
              {company.name}
            </span>
            <span className="text-[11px] text-gray-600 block mt-1">
              Data Directory: {company.dataDirectory}
            </span>
            <span className="text-[11px] text-gray-600 block">
              Company No: {company.number}
            </span>
          </div>

          <div className="p-3 flex-1 bg-[#f9fcfe] flex flex-col justify-end text-[11px] text-gray-600">
            <div className="border border-[#c6d7e6] p-2 bg-white rounded">
              <span className="font-bold text-gray-800 block">Quick Navigation Keys:</span>
              <span className="block mt-1"><b>V</b> - Vouchers (F4 to F9)</span>
              <span className="block"><b>K</b> - Day Book</span>
              <span className="block"><b>B</b> - Balance Sheet</span>
              <span className="block"><b>P</b> - Profit & Loss A/c</span>
              <span className="block"><b>T</b> - Trial Balance</span>
            </div>
          </div>
        </div>

        {/* Right Pane: Gateway Menu */}
        <div className="col-span-7 bg-white border border-[#1b569e] shadow flex flex-col text-xs text-gray-900">
          <div className="bg-[#1b569e] text-white font-bold px-3 py-1.5 text-center">
            GATEWAY OF TALLY
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {menuSections.map(sec => (
              <div key={sec.category}>
                <div className="text-[11px] font-bold text-gray-500 tracking-wider mb-1 px-3">
                  {sec.category}
                </div>
                <div className="space-y-0.5">
                  {sec.items.map(item => {
                    const currentIdx = runningItemIndex++;
                    const isSelected = selectedIdx === currentIdx;

                    return (
                      <div
                        key={item.label}
                        onClick={() => {
                          setSelectedIdx(currentIdx);
                          onNavigate(item.view);
                        }}
                        onMouseEnter={() => setSelectedIdx(currentIdx)}
                        className={`px-3 py-1.5 flex items-center justify-between cursor-pointer transition-colors ${
                          isSelected
                            ? 'bg-[#f7b928] text-black font-bold shadow-sm'
                            : 'hover:bg-[#fff9e6]'
                        }`}
                      >
                        <span>
                          {item.label.split('').map((char, charIdx) => {
                            if (char.toUpperCase() === item.key.toUpperCase()) {
                              return (
                                <span key={charIdx} className="text-[#105696] font-black underline">
                                  {char}
                                </span>
                              );
                            }
                            return char;
                          })}
                        </span>
                        <span className="text-[10px] text-gray-400 font-mono">
                          [{item.key}]
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="p-2 border-t border-gray-200 bg-gray-50 flex justify-between text-xs text-gray-600 px-4">
            <span>Quit (Esc)</span>
            <span>Select (Enter)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
