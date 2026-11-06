import React from 'react';
import { Company, LedgerMaster, Voucher } from '../types/accounting.ts';
import {
  generateTrialBalance,
  generateProfitAndLoss,
  generateBalanceSheet
} from '../engine/accounting.ts';
import { X, ArrowLeft } from 'lucide-react';

interface ReportViewProps {
  type: 'daybook' | 'trial-balance' | 'pnl' | 'balance-sheet';
  company: Company;
  ledgers: LedgerMaster[];
  vouchers: Voucher[];
  onBack: () => void;
}

export const ReportView: React.FC<ReportViewProps> = ({
  type,
  company,
  ledgers,
  vouchers,
  onBack
}) => {
  const trialBalance = generateTrialBalance(ledgers, vouchers);
  const pnl = generateProfitAndLoss(ledgers, vouchers);
  const balanceSheet = generateBalanceSheet(ledgers, vouchers);

  const getTitle = () => {
    switch (type) {
      case 'daybook':
        return 'Day Book';
      case 'trial-balance':
        return 'Trial Balance';
      case 'pnl':
        return 'Profit & Loss A/c';
      case 'balance-sheet':
        return 'Balance Sheet';
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#9cb3be] h-full select-none overflow-hidden font-sans">
      {/* Sub Header */}
      <div className="bg-[#9bc2d4] h-6 flex items-center justify-between px-3 text-xs font-semibold text-gray-800 border-b border-[#7ea1b2]">
        <div className="flex items-center space-x-2">
          <button onClick={onBack} className="hover:text-black" title="Back (Esc)">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span>{getTitle()} - {company.name}</span>
        </div>
        <button onClick={onBack} className="text-gray-700 hover:text-black font-bold p-0.5">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 p-3 overflow-hidden flex flex-col">
        <div className="flex-1 bg-white border border-[#1b569e] shadow flex flex-col overflow-hidden text-xs">
          {/* Header Bar */}
          <div className="bg-[#1b569e] text-white p-2 flex justify-between font-bold">
            <span>{getTitle().toUpperCase()}</span>
            <span>{company.name}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {/* Daybook View */}
            {type === 'daybook' && (
              <div>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#e4ecf3] border-b border-gray-300 text-[11px] font-semibold text-gray-700">
                      <th className="p-2 w-28">Date</th>
                      <th className="p-2">Particulars</th>
                      <th className="p-2 w-28 text-center">Vch Type</th>
                      <th className="p-2 w-24 text-center">Vch No.</th>
                      <th className="p-2 w-32 text-right">Debit (₹)</th>
                      <th className="p-2 w-32 text-right">Credit (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {vouchers.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-4 text-center text-gray-500 italic">
                          No transactions recorded yet. Press 'V' from Gateway to record vouchers.
                        </td>
                      </tr>
                    ) : (
                      vouchers.map(v => (
                        <tr key={v.id} className="hover:bg-yellow-50 cursor-pointer">
                          <td className="p-2 font-medium">{v.date}</td>
                          <td className="p-2">
                            <span className="font-bold text-[#105696] block">
                              {v.entries[0]?.ledgerName || 'Multiple Ledgers'}
                            </span>
                            {v.narration && (
                              <span className="text-[11px] text-gray-500 italic block">
                                {v.narration}
                              </span>
                            )}
                          </td>
                          <td className="p-2 text-center font-medium">{v.voucherType}</td>
                          <td className="p-2 text-center">{v.voucherNumber}</td>
                          <td className="p-2 text-right font-bold">
                            ₹{v.totalAmount.toLocaleString()}
                          </td>
                          <td className="p-2 text-right font-bold">
                            ₹{v.totalAmount.toLocaleString()}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Trial Balance View */}
            {type === 'trial-balance' && (
              <div>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#e4ecf3] border-b border-gray-300 text-[11px] font-semibold text-gray-700">
                      <th className="p-2">Particulars (Ledger Name)</th>
                      <th className="p-2 w-48">Group</th>
                      <th className="p-2 w-32 text-right">Debit (₹)</th>
                      <th className="p-2 w-32 text-right">Credit (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {trialBalance.items.map(item => (
                      <tr key={item.ledgerId} className="hover:bg-yellow-50">
                        <td className="p-2 font-semibold text-gray-900">{item.ledgerName}</td>
                        <td className="p-2 text-gray-600">{item.groupName}</td>
                        <td className="p-2 text-right font-bold text-gray-800">
                          {item.debit > 0 ? `₹${item.debit.toLocaleString()}` : '-'}
                        </td>
                        <td className="p-2 text-right font-bold text-gray-800">
                          {item.credit > 0 ? `₹${item.credit.toLocaleString()}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-gray-100 font-bold border-t-2 border-gray-400">
                      <td colSpan={2} className="p-2 text-right uppercase">Total:</td>
                      <td className="p-2 text-right text-[#105696] font-bold">
                        ₹{trialBalance.totalDebit.toLocaleString()}
                      </td>
                      <td className="p-2 text-right text-[#105696] font-bold">
                        ₹{trialBalance.totalCredit.toLocaleString()}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}

            {/* Profit & Loss View */}
            {type === 'pnl' && (
              <div className="grid grid-cols-2 gap-4">
                {/* Left Side: Expenses */}
                <div className="border border-gray-300 rounded p-3">
                  <h3 className="font-bold text-gray-800 border-b pb-1 mb-2">Expenses / Cost of Sales</h3>
                  <div className="space-y-1">
                    {pnl.tradingExpenses.map(e => (
                      <div key={e.ledgerName} className="flex justify-between">
                        <span>{e.ledgerName}</span>
                        <span className="font-semibold">₹{e.amount.toLocaleString()}</span>
                      </div>
                    ))}
                    {pnl.indirectExpenses.map(e => (
                      <div key={e.ledgerName} className="flex justify-between">
                        <span>{e.ledgerName}</span>
                        <span className="font-semibold">₹{e.amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Right Side: Income */}
                <div className="border border-gray-300 rounded p-3">
                  <h3 className="font-bold text-gray-800 border-b pb-1 mb-2">Incomes / Sales</h3>
                  <div className="space-y-1">
                    {pnl.tradingIncome.map(i => (
                      <div key={i.ledgerName} className="flex justify-between">
                        <span>{i.ledgerName}</span>
                        <span className="font-semibold">₹{i.amount.toLocaleString()}</span>
                      </div>
                    ))}
                    {pnl.indirectIncome.map(i => (
                      <div key={i.ledgerName} className="flex justify-between">
                        <span>{i.ledgerName}</span>
                        <span className="font-semibold">₹{i.amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Summary Row */}
                <div className="col-span-2 bg-[#f0f5fa] p-3 rounded flex justify-between items-center font-bold text-sm">
                  <span>Net Profit / (Loss):</span>
                  <span className={pnl.netProfit >= 0 ? 'text-green-700' : 'text-red-700'}>
                    ₹{pnl.netProfit.toLocaleString()}
                  </span>
                </div>
              </div>
            )}

            {/* Balance Sheet View */}
            {type === 'balance-sheet' && (
              <div className="grid grid-cols-2 gap-4">
                {/* Liabilities */}
                <div className="border border-gray-300 rounded p-3">
                  <h3 className="font-bold text-[#105696] border-b pb-1 mb-2">Liabilities</h3>
                  <div className="space-y-3">
                    {balanceSheet.liabilities.map(g => (
                      <div key={g.groupName}>
                        <div className="flex justify-between font-bold text-gray-800">
                          <span>{g.groupName}</span>
                          <span>₹{g.amount.toLocaleString()}</span>
                        </div>
                        {g.ledgers.map(l => (
                          <div key={l.name} className="flex justify-between pl-3 text-[11px] text-gray-600">
                            <span>{l.name}</span>
                            <span>₹{l.amount.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    ))}
                    <div className="flex justify-between font-bold text-green-700 border-t pt-1">
                      <span>Profit & Loss A/c (Net Profit)</span>
                      <span>₹{balanceSheet.profitOrLoss.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="mt-4 pt-2 border-t-2 border-gray-500 flex justify-between font-bold text-sm">
                    <span>Total Liabilities:</span>
                    <span>₹{balanceSheet.totalLiabilities.toLocaleString()}</span>
                  </div>
                </div>

                {/* Assets */}
                <div className="border border-gray-300 rounded p-3">
                  <h3 className="font-bold text-[#105696] border-b pb-1 mb-2">Assets</h3>
                  <div className="space-y-3">
                    {balanceSheet.assets.map(g => (
                      <div key={g.groupName}>
                        <div className="flex justify-between font-bold text-gray-800">
                          <span>{g.groupName}</span>
                          <span>₹{g.amount.toLocaleString()}</span>
                        </div>
                        {g.ledgers.map(l => (
                          <div key={l.name} className="flex justify-between pl-3 text-[11px] text-gray-600">
                            <span>{l.name}</span>
                            <span>₹{l.amount.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-2 border-t-2 border-gray-500 flex justify-between font-bold text-sm">
                    <span>Total Assets:</span>
                    <span>₹{balanceSheet.totalAssets.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-2 border-t border-gray-300 bg-gray-50 flex justify-end">
            <button
              onClick={onBack}
              className="px-4 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold"
            >
              Back (Esc)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
