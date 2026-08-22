// frontend/components/DecisionCard.tsx
"use client";

import { useState } from "react";
import { CheckCircle, XCircle, Package, User, Clock, AlertCircle, MessageSquare } from "lucide-react";

interface Donation {
  id: string;
  donor: string;
  items: string[];
  quantity: number;
  notes: string;
  status: string;
}

export default function DecisionCard({ donation }: { donation: Donation }) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const [dispatchInfo, setDispatchInfo] = useState<any>(null); // Capture the dispatch agent's output

  const handleAction = async (action: "approve" | "reject") => {
    setIsProcessing(true);
    try {
      if (action === "approve") {
        const res = await fetch(`http://127.0.0.1:8000/api/approve/${donation.id}`, {
          method: "POST",
        });
        const data = await res.json();
        setActionResult(`✅ ${data.message}`);
        setDispatchInfo(data.dispatch); // Capture the dispatch agent's output
      } else {
        setActionResult("❌ Donation rejected and removed from queue.");
      }
    } catch (error) {
      setActionResult("⚠️ Error processing action. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  // SUCCESS STATE: Shows approval + Multi-Agent Dispatch Handoff
  if (actionResult) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex items-center gap-3 text-green-700 font-medium mb-4">
          <CheckCircle className="w-5 h-5" />
          <span>{actionResult}</span>
        </div>
        
        {dispatchInfo && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Dispatch Agent Action</span>
              <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-semibold rounded-full">SMS Drafted</span>
            </div>
            <p className="text-sm text-gray-700 mb-2">
              Routed to <span className="font-semibold text-gray-900">{dispatchInfo.volunteer_name}</span> ({dispatchInfo.volunteer_phone})
            </p>
            <div className="bg-white p-3 rounded border border-gray-200 text-sm text-gray-700 italic shadow-sm">
              "{dispatchInfo.drafted_sms}"
            </div>
          </div>
        )}
      </div>
    );
  }

  // PENDING STATE: Shows Agent Reasoning and Approval Gates
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden mb-4 transition-all hover:shadow-xl">
      {/* Header */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Donation {donation.id}</h3>
        </div>
        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full uppercase tracking-wide">
          Awaiting Approval
        </span>
      </div>

      <div className="p-6">
        {/* Agent Reasoning Block (The "Transparency" Winner) */}
        <div className="mb-6 bg-blue-50 border border-blue-100 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-blue-900 mb-1">Agent Reasoning</h4>
              <p className="text-sm text-blue-800">
                I have parsed the incoming SMS, extracted the donor details and inventory items, 
                and drafted an IRS-compliant receipt. This donation is ready to be added to active inventory.
              </p>
            </div>
          </div>
        </div>

        {/* Extracted Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="flex items-start gap-3">
            <User className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Donor</p>
              <p className="text-gray-900 font-medium">{donation.donor}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Drop-off Time</p>
              <p className="text-gray-900 font-medium">{donation.notes.replace("Dropoff at ", "")}</p>
            </div>
          </div>
          <div className="md:col-span-2">
            <p className="text-xs text-gray-500 uppercase font-semibold mb-2">Items Logged</p>
            <div className="flex flex-wrap gap-2">
              {donation.items.map((item, idx) => (
                <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md border border-gray-200">
                  {item}
                </span>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Total Estimated Quantity: <span className="font-semibold text-gray-900">{donation.quantity} units</span></p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-100">
          <button
            onClick={() => handleAction("approve")}
            disabled={isProcessing}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            {isProcessing ? "Processing..." : <><CheckCircle className="w-4 h-4" /> Approve & Log</>}
          </button>
          <button
            onClick={() => handleAction("reject")}
            disabled={isProcessing}
            className="flex-1 bg-white hover:bg-red-50 text-red-600 border border-red-200 font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <XCircle className="w-4 h-4" /> Reject
          </button>
        </div>
      </div>
    </div>
  );
}