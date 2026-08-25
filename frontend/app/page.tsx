// frontend/app/page.tsx
"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Package, Inbox } from "lucide-react";
import { motion } from "framer-motion";
import DecisionCard from "../components/DecisionCard";
import StatusBadge, { AgentStatus } from "../components/StatusBadge";
import ObservabilityDashboard from "../components/ObservabilityDashboard";

interface Donation {
  id: string;
  donor: string;
  items: string[];
  quantity: number;
  notes: string;
  status: string;
  donor_email?: string;
  donor_phone?: string;
  source?: string;
}

export default function Home() {
  const [pendingDonations, setPendingDonations] = useState<Donation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPending = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/pending-approvals");
      const data = await res.json();
      setPendingDonations(data.pending || []);
    } catch (error) {
      console.error("Failed to fetch pending approvals:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const processQueueAndRefresh = async () => {
    setIsLoading(true);
    try {
      // 1. Tell backend to scan folders, process new files, and move them to processed_*
      const res = await fetch("http://localhost:8000/api/scan-queue", { method: "POST" });
      const data = await res.json();
      
      if (data.status === "success") {
        console.log(`Processed ${data.processed_count} items from queue.`);
      }
      
      // 2. Fetch the newly created donations
      await fetchPending();
    } catch (error) {
      console.error("Queue processing failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch pending items on load, don't process queue
    fetchPending();
  }, []);

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
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div 
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 md:gap-6 mb-10"
        >
          <div className="flex-1">
            <motion.h1 className="text-4xl font-extrabold text-gray-900 flex items-center gap-3">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ repeat: Infinity, duration: 5, repeatDelay: 10 }}
              >
                <Package className="w-10 h-10 text-blue-600" />
              </motion.div>
              PantryPilot Dashboard
            </motion.h1>
            <p className="text-gray-600 mt-2 text-lg whitespace-nowrap">Automated file-queue processing (SMS → Email → Voice)</p>
          </div>
          
          <div className="flex items-center gap-4">
            <StatusBadge status={systemStatus} />
            
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={processQueueAndRefresh}
              disabled={isLoading}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl shadow-sm hover:shadow-md font-medium disabled:opacity-50 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
              {isLoading ? "Processing Queue..." : "Process Queue & Refresh"}
            </motion.button>
          </div>
        </motion.div>

        {/* Queue Instructions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 bg-blue-50 border border-blue-200 rounded-2xl p-6 shadow-sm"
        >
          <h2 className="text-lg font-bold text-blue-900 mb-2 flex items-center gap-2">
            <Inbox className="w-5 h-5" />
            How to Add New Donations
          </h2>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li><strong>SMS:</strong> Drop a <code className="bg-blue-100 px-1 rounded">.txt</code> file into <code className="bg-blue-100 px-1 rounded">received_messages/sms/new_sms/</code></li>
            <li><strong>Email:</strong> Drop a <code className="bg-blue-100 px-1 rounded">.txt</code> file (e.g., <code className="bg-blue-100 px-1 rounded">donor@email.com.txt</code>) into <code className="bg-blue-100 px-1 rounded">received_messages/email/new_email/</code></li>
            <li><strong>Voice:</strong> Drop an audio file (<code className="bg-blue-100 px-1 rounded">.webm</code>, <code className="bg-blue-100 px-1 rounded">.wav</code>, <code className="bg-blue-100 px-1 rounded">.mp3</code>) into <code className="bg-blue-100 px-1 rounded">received_messages/voice/new_voice/</code></li>
          </ul>
          <p className="text-sm text-blue-700 mt-3 font-medium">
            Click "Process Queue & Refresh" above to transcribe voice with Qwen, parse all messages, and move files to the processed folders.
          </p>
        </motion.div>

        {/* Content Area */}
        {isLoading && pendingDonations.length === 0 ? (
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
            <h3 className="text-lg font-semibold text-gray-900">Queue Empty!</h3>
            <p className="text-gray-500 mt-1">Drop files into the received_messages folders, then click Process Queue.</p>
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

        {/* Observability Dashboard */}
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