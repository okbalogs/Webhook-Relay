"use client";

import React, { useState } from "react";
import { Server, Copy, Check, Trash2, Globe } from "lucide-react";

export interface Endpoint {
  id: string;
  name: string;
  secret_key: string;
  provider: "stripe" | "github" | "shopify" | "generic";
  target_url: string;
  ingest_url: string;
  is_active: boolean;
  max_retries: number;
  timeout_seconds: number;
}

interface EndpointManagerProps {
  endpoints: Endpoint[];
  selectedEndpointId: string | null;
  onSelectEndpoint: (id: string | null) => void;
  onDeleteEndpoint: (id: string) => void;
  onCreateEndpoint: (data: any) => void;
  isOpenModal: boolean;
  onCloseModal: () => void;
}

export const EndpointManager: React.FC<EndpointManagerProps> = ({
  endpoints,
  selectedEndpointId,
  onSelectEndpoint,
  onDeleteEndpoint,
  onCreateEndpoint,
  isOpenModal,
  onCloseModal,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    provider: "generic",
    target_url: "http://localhost:3000/api/webhook",
    secret_key: "",
    max_retries: 5,
    timeout_seconds: 10,
  });

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreateEndpoint(formData);
    setFormData({
      name: "",
      provider: "generic",
      target_url: "http://localhost:3000/api/webhook",
      secret_key: "",
      max_retries: 5,
      timeout_seconds: 10,
    });
    onCloseModal();
  };

  const selectedEndpoint = endpoints.find((e) => e.id === selectedEndpointId);

  return (
    <div className="space-y-4">
      {/* Endpoint Selector Tabs */}
      <div className="flex items-center justify-between border-b border-dark-700 pb-3">
        <div className="flex items-center space-x-2 overflow-x-auto pb-1">
          <button
            onClick={() => onSelectEndpoint(null)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedEndpointId === null
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "bg-dark-800 text-gray-400 hover:text-gray-200 hover:bg-dark-700"
            }`}
          >
            All Ingested Events ({endpoints.length})
          </button>
          {endpoints.map((ep) => (
            <button
              key={ep.id}
              onClick={() => onSelectEndpoint(ep.id)}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all border ${
                selectedEndpointId === ep.id
                  ? "bg-dark-700 border-indigo-500 text-indigo-300"
                  : "bg-dark-800 border-dark-700 text-gray-400 hover:text-gray-200"
              }`}
            >
              <span className="uppercase text-[10px] px-1.5 py-0.2 bg-dark-900 rounded border border-dark-600 font-mono">
                {ep.provider}
              </span>
              <span>{ep.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Selected Endpoint Banner Info */}
      {selectedEndpoint && (
        <div className="bg-dark-800/90 border border-dark-700 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-sm text-gray-200">{selectedEndpoint.name}</h3>
              <span className="text-xs px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded font-mono uppercase">
                {selectedEndpoint.provider}
              </span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-400 font-mono">
              <Globe className="w-3.5 h-3.5 text-gray-500" />
              <span>Target: {selectedEndpoint.target_url}</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="bg-dark-900 border border-dark-600 rounded-lg px-3 py-1.5 flex items-center space-x-2 text-xs font-mono text-gray-300">
              <span className="text-gray-500">Ingest Proxy:</span>
              <span className="text-indigo-400 font-medium">{selectedEndpoint.ingest_url}</span>
              <button
                onClick={() => copyToClipboard(selectedEndpoint.ingest_url, `ingest-${selectedEndpoint.id}`)}
                className="hover:text-white p-1"
                title="Copy Ingest URL"
              >
                {copiedId === `ingest-${selectedEndpoint.id}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            <button
              onClick={() => onDeleteEndpoint(selectedEndpoint.id)}
              className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors border border-rose-500/20"
              title="Delete Endpoint"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Modal to Create Endpoint */}
      {isOpenModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-dark-800 border border-dark-700 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-lg font-bold text-gray-100 flex items-center space-x-2">
              <Server className="w-5 h-5 text-indigo-400" />
              <span>Create Webhook Proxy Ingestion Endpoint</span>
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-gray-400 mb-1 font-medium">Endpoint Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Stripe Production Payments"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1 font-medium">Webhook Provider Type</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value as any })}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="stripe">Stripe (Stripe-Signature HMAC)</option>
                  <option value="github">GitHub (X-Hub-Signature-256)</option>
                  <option value="shopify">Shopify (X-Shopify-Hmac-SHA256)</option>
                  <option value="generic">Generic (Custom Secret / HMAC)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-400 mb-1 font-medium">Target URL (Destination / Local Tunnel)</label>
                <input
                  type="text"
                  required
                  placeholder="http://localhost:3000/api/webhook"
                  value={formData.target_url}
                  onChange={(e) => setFormData({ ...formData, target_url: e.target.value })}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1 font-medium">Signing Secret Key (Optional)</label>
                <input
                  type="text"
                  placeholder="whsec_..."
                  value={formData.secret_key}
                  onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1 font-medium">Max Retries</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.max_retries}
                    onChange={(e) => setFormData({ ...formData, max_retries: parseInt(e.target.value) || 5 })}
                    className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1 font-medium">Timeout (seconds)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={formData.timeout_seconds}
                    onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) || 10 })}
                    className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-dark-700">
                <button
                  type="button"
                  onClick={onCloseModal}
                  className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-md shadow-indigo-600/20"
                >
                  Create Endpoint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

