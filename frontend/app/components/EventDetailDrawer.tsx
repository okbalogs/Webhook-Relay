"use client";

import React, { useState } from "react";
import { X, Play, Code, CheckCircle, AlertTriangle, Clock, RefreshCw, FileText, Activity } from "lucide-react";

export interface DeliveryAttemptDetail {
  id: string;
  attempt_count: number;
  status: string;
  response_status: number | null;
  execution_duration_ms: number | null;
  error_message: string | null;
  next_retry_at: string | null;
  created_at: string;
}

export interface EventDetail {
  id: string;
  endpoint_id: string;
  provider: string;
  event_type: string | null;
  headers: Record<string, any>;
  payload: Record<string, any>;
  raw_body: string;
  signature_valid: boolean;
  created_at: string;
  attempts: DeliveryAttemptDetail[];
}

interface EventDetailDrawerProps {
  eventDetail: EventDetail | null;
  onClose: () => void;
  onOpenReplayModal: (event: EventDetail) => void;
}

export const EventDetailDrawer: React.FC<EventDetailDrawerProps> = ({
  eventDetail,
  onClose,
  onOpenReplayModal,
}) => {
  const [activeTab, setActiveTab] = useState<"payload" | "headers" | "attempts" | "raw">("payload");

  if (!eventDetail) return null;

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-5 shadow-2xl space-y-4">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-dark-700 pb-3">
        <div className="flex items-center space-x-3">
          <span className="uppercase text-xs font-bold px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded font-mono">
            {eventDetail.provider}
          </span>
          <h2 className="text-sm font-bold text-gray-100 font-mono">
            {eventDetail.event_type || "generic.event"}
          </h2>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => onOpenReplayModal(eventDetail)}
            className="flex items-center space-x-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all shadow-md shadow-indigo-600/20"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Replay Request</span>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-white rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-dark-700 text-xs">
        <button
          onClick={() => setActiveTab("payload")}
          className={`pb-2 px-3 font-medium transition-colors border-b-2 ${
            activeTab === "payload"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          JSON Payload
        </button>
        <button
          onClick={() => setActiveTab("headers")}
          className={`pb-2 px-3 font-medium transition-colors border-b-2 ${
            activeTab === "headers"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          Headers ({Object.keys(eventDetail.headers || {}).length})
        </button>
        <button
          onClick={() => setActiveTab("attempts")}
          className={`pb-2 px-3 font-medium transition-colors border-b-2 flex items-center space-x-1 ${
            activeTab === "attempts"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <span>Delivery Log</span>
          <span className="px-1.5 py-0.2 bg-dark-900 rounded-full text-[10px] font-mono border border-dark-600">
            {eventDetail.attempts.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab("raw")}
          className={`pb-2 px-3 font-medium transition-colors border-b-2 ${
            activeTab === "raw"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          Raw Body
        </button>
      </div>

      {/* Tab Contents */}
      <div className="text-xs">
        {activeTab === "payload" && (
          <pre className="bg-dark-900 border border-dark-700 rounded-lg p-4 font-mono text-emerald-400 overflow-x-auto max-h-96">
            {JSON.stringify(eventDetail.payload, null, 2)}
          </pre>
        )}

        {activeTab === "headers" && (
          <div className="bg-dark-900 border border-dark-700 rounded-lg p-4 font-mono space-y-2 max-h-96 overflow-y-auto">
            {Object.entries(eventDetail.headers || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between border-b border-dark-800 pb-1">
                <span className="text-indigo-400 font-semibold">{k}:</span>
                <span className="text-gray-300 truncate max-w-md">{String(v)}</span>
              </div>
            ))}
          </div>
        )}

        {activeTab === "attempts" && (
          <div className="space-y-3">
            {eventDetail.attempts.map((att) => {
              const isSuccess = att.status === "success";
              const isFailed = att.status === "failed" || att.status === "exhausted";

              return (
                <div
                  key={att.id}
                  className="bg-dark-900 border border-dark-700 rounded-lg p-3 space-y-2 font-mono"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-gray-300">Attempt #{att.attempt_count}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isSuccess 
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
                          : isFailed
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse"
                      }`}>
                        {att.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3 text-gray-400 text-[11px]">
                      {att.response_status && (
                        <span className={att.response_status >= 200 && att.response_status < 300 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                          HTTP {att.response_status}
                        </span>
                      )}
                      {att.execution_duration_ms !== null && (
                        <span>{att.execution_duration_ms} ms</span>
                      )}
                    </div>
                  </div>

                  {att.error_message && (
                    <p className="text-rose-400 text-[11px] bg-rose-500/10 p-2 rounded border border-rose-500/20">
                      {att.error_message}
                    </p>
                  )}

                  {att.next_retry_at && att.status === "retrying" && (
                    <div className="flex items-center space-x-1.5 text-amber-400 text-[11px]">
                      <Clock className="w-3 h-3 animate-spin" />
                      <span>Next retry scheduled: {new Date(att.next_retry_at).toLocaleTimeString()}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {activeTab === "raw" && (
          <pre className="bg-dark-900 border border-dark-700 rounded-lg p-4 font-mono text-gray-300 overflow-x-auto max-h-96 whitespace-pre-wrap">
            {eventDetail.raw_body}
          </pre>
        )}
      </div>
    </div>
  );
};

