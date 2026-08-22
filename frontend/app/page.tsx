// frontend/app/page.tsx
"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Package } from "lucide-react";
import DecisionCard from "../components/DecisionCard";

interface Donation {
  id: string;
  donor: string;
  items: string[];
  quantity: number;
  notes: string;
  status: string;
}

export default function Home() {
  const [pendingDonations, setPendingDonations] = useState<Donation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPending = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/pending-approvals");
      const data = await res.json();
      setPendingDonations(data.pending || []);
    } catch (error) {
      console.error("Failed to fetch pending approvals:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Package className="w-8 h-8 text-blue-600" />
              PantryPilot Dashboard
            </h1>
            <p className="text-gray-600 mt-1">Quiet until it matters. Review and approve agent actions.</p>
          </div>
          <button 
            onClick={fetchPending}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Content Area */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : pendingDonations.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900">All caught up!</h3>
            <p className="text-gray-500 mt-1">No pending donations awaiting your approval.</p>
          </div>
        ) : (
          <div>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              Pending Approvals ({pendingDonations.length})
            </h2>
            {pendingDonations.map((donation) => (
              <DecisionCard key={donation.id} donation={donation} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}