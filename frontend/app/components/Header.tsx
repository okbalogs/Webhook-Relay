"use client";

import React from "react";
import { Activity, Radio, Plus, Server, RefreshCw } from "lucide-react";

interface HeaderProps {
  sseConnected: boolean;
  onOpenCreateEndpoint: () => void;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ sseConnected, onOpenCreateEndpoint, onRefresh }) => {
  return (
    <header className="border-b border-dark-700 bg-dark-800/80 backdrop-blur-md sticky top-0 z-30 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-lg text-white shadow-lg shadow-indigo-500/20">
          <Activity className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-gray-100 flex items-center space-x-2">
            <span>Webhook Relay & Replay</span>
            <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-mono font-medium">
              v1.0.0
            </span>
          </h1>
          <p className="text-xs text-gray-400">Self-hosted Ingestion, HMAC Verification & Exponential Retry Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* SSE Status Badge */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-medium transition-all ${
          sseConnected 
            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
            : "bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse"
        }`}>
          <Radio className={`w-3.5 h-3.5 ${sseConnected ? "animate-pulse text-emerald-400" : ""}`} />
          <span>{sseConnected ? "SSE Stream Connected" : "Connecting SSE..."}</span>
        </div>

        <button
          onClick={onRefresh}
          className="p-2 text-gray-400 hover:text-gray-200 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors border border-dark-600"
          title="Refresh Events"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        <button
          onClick={onOpenCreateEndpoint}
          className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Endpoint</span>
        </button>
      </div>
    </header>
  );
};

