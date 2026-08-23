// frontend/app/page.tsx
"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Package } from "lucide-react";
import { motion } from "framer-motion";
import DecisionCard from "../components/DecisionCard";
import StatusBadge, { AgentStatus } from "../components/StatusBadge";
import ObservabilityDashboard from "../components/ObservabilityDashboard"; // <-- Added import

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

  // Determine the overall system status based on the data
  const systemStatus: AgentStatus = isLoading 
    ? "thinking" 
    : pendingDonations.length > 0 
      ? "awaiting_approval" 
      : "idle";

  return (
    <motion.main 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gray-50 p-8"
    >
      {/* Changed to max-w-4xl to give the observability dashboard a bit more breathing room */}
      <div className="max-w-4xl mx-auto">
        {/* Animated Header with Status Badge */}
        <motion.div 
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="flex justify-between items-center mb-10"
        >
          <div>
            <motion.h1 className="text-4xl font-extrabold text-gray-900 flex items-center gap-3">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ repeat: Infinity, duration: 5, repeatDelay: 10 }}
              >
                <Package className="w-10 h-10 text-blue-600" />
              </motion.div>
              PantryPilot Dashboard
            </motion.h1>
            <p className="text-gray-600 mt-2 text-lg">Quiet until it matters. Review and approve agent actions.</p>
          </div>
          
          {/* Status Badge and Refresh Button */}
          <div className="flex items-center gap-4">
            <StatusBadge status={systemStatus} />
            
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={fetchPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm hover:shadow-md font-medium"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </motion.button>
          </div>
        </motion.div>

        {/* Content Area */}
        {isLoading ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-center items-center h-64"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"
            />
          </motion.div>
        ) : pendingDonations.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm"
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 3, repeatDelay: 2 }}
              className="inline-block mb-4"
            >
              <Package className="w-16 h-16 text-gray-300" />
            </motion.div>
            <h3 className="text-lg font-semibold text-gray-900">All caught up!</h3>
            <p className="text-gray-500 mt-1">No pending donations awaiting your approval.</p>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              Pending Approvals ({pendingDonations.length})
            </h2>
            {pendingDonations.map((donation) => (
              <DecisionCard key={donation.id} donation={donation} />
            ))}
          </motion.div>
        )}

        {/* Observability Dashboard Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12"
        >
          <ObservabilityDashboard />
        </motion.div>

      </div>
    </motion.main>
  );
}