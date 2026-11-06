import React from 'react';

interface StatusBarProps {
  onQuit?: () => void;
  message?: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({ onQuit, message }) => {
  return (
    <footer className="h-7 bg-[#d9e6ed] border-t border-[#adc2ce] flex items-center justify-between text-xs text-gray-700 select-none px-2 font-mono">
      <div className="flex items-center space-x-2">
        <button
          onClick={onQuit}
          className="bg-white border border-[#9bb8ca] px-3 py-0.5 rounded shadow-sm text-xs font-semibold text-gray-800 hover:bg-yellow-100 transition-colors"
        >
          <span className="text-[#105696] font-bold underline">Q</span>: Quit
        </button>
        <span className="text-gray-400 font-normal">^</span>
        {message && <span className="text-[#105696] font-semibold ml-2">{message}</span>}
      </div>

      <div className="flex items-center space-x-1 divide-x divide-gray-300">
        <span className="px-3 py-0.5 bg-white border border-gray-300 rounded shadow-sm text-[11px] font-sans">
          Ctrl + M: Gateway
        </span>
        <span className="px-3 py-0.5 bg-white border border-gray-300 rounded shadow-sm text-[11px] font-sans">
          Alt + K: Company
        </span>
        <span className="px-3 py-0.5 bg-white border border-gray-300 rounded shadow-sm text-[11px] font-sans">
          Esc: Back
        </span>
      </div>
    </footer>
  );
};
