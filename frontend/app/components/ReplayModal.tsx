"use client";

import React, { useState } from "react";
import { Play, RotateCcw, X, AlertCircle } from "lucide-react";
import { EventDetail } from "./EventDetailDrawer";

interface ReplayModalProps {
  event: EventDetail | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmReplay: (eventId: string, overridePayload: any, overrideTargetUrl: string) => void;
}

export const ReplayModal: React.FC<ReplayModalProps> = ({
  event,
  isOpen,
  onClose,
  onConfirmReplay,
}) => {
  if (!isOpen || !event) return null;

  const [payloadText, setPayloadText] = useState(JSON.stringify(event.payload, null, 2));
  const [targetUrl, setTargetUrl] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleReplay = () => {
    try {
      const parsed = JSON.parse(payloadText);
      setErrorMsg(null);
      onConfirmReplay(event.id, parsed, targetUrl);
      onClose();
    } catch (err) {
      setErrorMsg("Invalid JSON syntax in payload editor");
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-dark-800 border border-dark-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 text-xs">
        <div className="flex items-center justify-between border-b border-dark-700 pb-3">
          <div className="flex items-center space-x-2">
            <RotateCcw className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-gray-100">Replay Webhook Payload</h2>
          </div>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-gray-400">
          Modify the payload or target URL below to test edge cases, exception handling, or local debugging routes.
        </p>

        {errorMsg && (
          <div className="flex items-center space-x-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 p-2.5 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div>
          <label className="block text-gray-400 mb-1 font-medium">Override Target URL (Optional)</label>
          <input
            type="text"
            placeholder="http://localhost:3000/api/webhook"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 font-mono focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-gray-400 mb-1 font-medium">JSON Payload</label>
          <textarea
            rows={10}
            value={payloadText}
            onChange={(e) => setPayloadText(e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg p-3 text-emerald-400 font-mono focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-dark-700">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleReplay}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-md shadow-indigo-600/20"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Re-fire Request</span>
          </button>
        </div>
      </div>
    </div>
  );
};

