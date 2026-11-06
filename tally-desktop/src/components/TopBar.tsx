import React from 'react';
import { Bell, Minus, Square, X, Search } from 'lucide-react';

interface TopBarProps {
  onCompanyClick?: () => void;
  onGoToClick?: () => void;
  onHelpClick?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onCompanyClick, onGoToClick, onHelpClick }) => {
  return (
    <header className="bg-[#102d36] text-white flex flex-col select-none border-b border-[#234b56]">
      {/* Top row */}
      <div className="flex items-center justify-between px-3 py-1.5 h-11">
        {/* Left: Tally Prime Edit Log EDU Logo */}
        <div className="flex items-center space-x-2">
          <div className="flex items-baseline">
            <span className="text-2xl font-black italic tracking-tighter text-[#4bd3e6] font-serif">
              Tally
            </span>
            <span className="text-xl font-bold ml-1 tracking-tight text-white">
              Prime
            </span>
          </div>
          <div className="flex flex-col text-[10px] leading-tight text-gray-200 border-l border-gray-600 pl-2">
            <span className="text-gray-300">Edit Log</span>
            <span className="font-bold text-white text-xs tracking-wider">EDU</span>
          </div>
        </div>

        {/* Center: Search Bar with Alt+G / Alt+F */}
        <div className="flex-1 max-w-xl mx-4">
          <div className="flex items-center bg-[#173a45] hover:bg-[#1a424f] border border-[#2b5a68] rounded px-3 py-1 text-xs text-gray-300 shadow-inner">
            <Search className="w-3.5 h-3.5 text-gray-400 mr-2" />
            <input
              type="text"
              readOnly
              placeholder="Find details entered in masters and transactions. (Alt+F)"
              className="bg-transparent flex-1 outline-none text-xs text-gray-200 placeholder-gray-400 cursor-pointer"
              onClick={onGoToClick}
            />
          </div>
        </div>

        {/* Right: Notification and Window Controls */}
        <div className="flex items-center space-x-4 text-gray-300">
          <button title="Notifications" className="hover:text-white transition-colors">
            <Bell className="w-4 h-4" />
          </button>
          <div className="flex items-center space-x-2 border-l border-gray-700 pl-3">
            <button
              onClick={() => (window as any).electronAPI?.minimize?.()}
              className="p-1 hover:bg-[#1d4451] rounded"
              title="Minimize"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => (window as any).electronAPI?.maximize?.()}
              className="p-1 hover:bg-[#1d4451] rounded"
              title="Maximize"
            >
              <Square className="w-3 h-3" />
            </button>
            <button
              onClick={() => (window as any).electronAPI?.close?.()}
              className="p-1 hover:bg-red-700 text-gray-300 hover:text-white rounded"
              title="Close"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Menu Row with Underlined Hotkeys */}
      <nav className="flex items-center justify-between px-4 py-1 bg-[#13353f] border-t border-[#1d4754] text-[13px] font-medium text-gray-200">
        <div className="flex items-center space-x-6">
          <button
            onClick={onCompanyClick}
            className="hover:text-yellow-400 transition-colors focus:outline-none"
          >
            <span className="underline decoration-1 underline-offset-2 font-bold">K</span>: Company
          </button>
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">Y</span>: Data
          </button>
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">Z</span>: Exchange
          </button>
        </div>

        {/* Center Button: G: Go To */}
        <div className="flex justify-center">
          <button
            onClick={onGoToClick}
            className="bg-white text-[#102d36] font-semibold text-xs px-5 py-0.5 rounded shadow hover:bg-gray-100 transition-colors"
          >
            <span className="underline decoration-1 underline-offset-2 font-bold">G</span>: Go To
          </button>
        </div>

        {/* Right Menu Items */}
        <div className="flex items-center space-x-6">
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">O</span>: Import
          </button>
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">E</span>: Export
          </button>
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">M</span>: Share
          </button>
          <button className="hover:text-yellow-400 transition-colors focus:outline-none">
            <span className="underline decoration-1 underline-offset-2 font-bold">P</span>: Print
          </button>
          <button
            onClick={onHelpClick}
            className="hover:text-yellow-400 transition-colors focus:outline-none"
          >
            <span className="underline decoration-1 underline-offset-2 font-bold">F1</span>: Help
          </button>
        </div>
      </nav>
    </header>
  );
};
