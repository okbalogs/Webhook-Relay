"use client";

import React from "react";
import { CheckCircle2, XCircle, AlertCircle, Clock, RotateCw, ChevronRight } from "lucide-react";

export interface WebhookEventItem {
  id: string;
  endpoint_id: string;
  provider: string;
  event_type: string | null;
  signature_valid: boolean;
  created_at: string;
}

interface EventLogTableProps {
  events: WebhookEventItem[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

export const EventLogTable: React.FC<EventLogTableProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
}) => {
  if (events.length === 0) {
    return (
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-12 text-center space-y-3">
        <Clock className="w-10 h-10 text-gray-500 mx-auto animate-pulse" />
        <h3 className="text-sm font-semibold text-gray-300">Listening for Inbound Webhooks</h3>
        <p className="text-xs text-gray-500 max-w-sm mx-auto">
          Send webhooks to your generated proxy ingestion URL to inspect headers, payloads, HMAC signatures, and retry logs in real time.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl overflow-hidden shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-dark-700 bg-dark-900/60 text-gray-400 font-medium">
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">Signature Validation</th>
              <th className="py-3 px-4">Ingestion Time</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-700/60 text-gray-300 font-mono">
            {events.map((ev) => {
              const isSelected = selectedEventId === ev.id;
              const formattedTime = new Date(ev.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              });

              return (
                <tr
                  key={ev.id}
                  onClick={() => onSelectEvent(ev.id)}
                  className={`hover:bg-dark-700/50 cursor-pointer transition-colors ${
                    isSelected ? "bg-dark-700/80 border-l-4 border-l-indigo-500" : ""
                  }`}
                >
                  <td className="py-3 px-4">
                    <span className="uppercase text-[10px] px-2 py-0.5 bg-dark-900 text-indigo-300 rounded border border-dark-600 font-semibold">
                      {ev.provider}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-gray-200">
                    {ev.event_type || "generic.event"}
                  </td>
                  <td className="py-3 px-4">
                    {ev.signature_valid ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-sans font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        <span>HMAC Verified</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-sans font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <XCircle className="w-3 h-3 text-rose-400" />
                        <span>Invalid Signature</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-gray-400 font-sans text-xs">
                    {formattedTime}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button className="text-gray-400 hover:text-white p-1">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

