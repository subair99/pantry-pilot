// frontend/components/DecisionCard.tsx
"use client";

import { useState } from "react";
import { CheckCircle, XCircle, Package, User, Clock, AlertCircle, MessageSquare, Sparkles, TrendingUp, Mail } from "lucide-react";
import { motion, Variants } from "framer-motion";

interface Donation {
  id: string;
  donor: string;
  items: string[];
  quantity: number;
  notes: string;
  status: string;
  donor_email?: string;
  donor_phone?: string;
  source?: string; // Added for explicit channel detection
}

// 1. Explicitly type the variants to satisfy TypeScript
const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95,
    transition: { duration: 0.3 }
  }
};

const reasoningBoxVariants: Variants = {
  hidden: { opacity: 0, x: -10 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { delay: 0.2, duration: 0.6, ease: "easeOut" }
  }
};

const buttonVariants = {
  hover: { scale: 1.02, transition: { duration: 0.2 } },
  tap: { scale: 0.98 },
};

export default function DecisionCard({ donation }: { donation: Donation }) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const [dispatchInfo, setDispatchInfo] = useState<any>(null);
  const [logisticsInfo, setLogisticsInfo] = useState<any>(null);

  const handleAction = async (action: "approve" | "reject") => {
    setIsProcessing(true);
    try {
      if (action === "approve") {
        const res = await fetch(`http://127.0.0.1:8000/api/approve/${donation.id}`, {
          method: "POST",
        });
        const data = await res.json();
        setActionResult(`✅ ${data.message}`);
        setDispatchInfo(data.dispatch);
        setLogisticsInfo(data.logistics);
      } else {
        setActionResult("❌ Donation rejected and removed from queue.");
      }
    } catch (error) {
      setActionResult("⚠️ Error processing action. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  // SUCCESS STATE
  if (actionResult) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white p-6 rounded-2xl shadow-lg border border-green-200 mb-4"
      >
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 500, delay: 0.1 }}
          className="flex items-center gap-3 text-green-700 font-semibold mb-6"
        >
          <CheckCircle className="w-6 h-6" />
          <span className="text-lg">{actionResult}</span>
        </motion.div>
        
        {/* SMS Dispatch Block */}
        {dispatchInfo && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="bg-gradient-to-br from-gray-50 to-blue-50/50 border border-blue-200 rounded-xl p-5 shadow-sm"
          >
            <div className="flex items-center gap-2 mb-4">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
              >
                <MessageSquare className="w-5 h-5 text-blue-600" />
              </motion.div>
              <span className="text-xs font-bold text-blue-900 uppercase tracking-wider">Dispatch Agent Action</span>
              <motion.span 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: "spring" }}
                className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full shadow-sm"
              >
                SMS Sent
              </motion.span>
            </div>
            <p className="text-sm text-gray-700 mb-3">
              Routed to <span className="font-bold text-gray-900">{dispatchInfo.volunteer_name}</span> 
              <span className="text-gray-500 ml-1">({dispatchInfo.volunteer_phone})</span>
            </p>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="bg-white p-4 rounded-lg border border-blue-100 text-sm text-gray-700 shadow-inner italic"
            >
              "{dispatchInfo.drafted_sms}"
            </motion.div>
          </motion.div>
        )}

        {/* NEW: Email Tax Receipt Block */}
        {dispatchInfo && dispatchInfo.email_response && dispatchInfo.email_response.status !== "skipped" && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="mt-4 bg-gradient-to-br from-gray-50 to-indigo-50/50 border border-indigo-200 rounded-xl p-5 shadow-sm"
          >
            <div className="flex items-center gap-2 mb-3">
              <Mail className="w-5 h-5 text-indigo-600" />
              <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider">Dispatch Agent Action</span>
              <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-bold rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Tax Receipt Sent
              </span>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <p className="text-sm text-gray-700">
                Sent to <span className="font-semibold text-gray-900">{dispatchInfo.donor_email}</span>
              </p>
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" /> Delivered just now
              </span>
            </div>

            <div className="bg-white p-4 rounded-lg border border-indigo-100 shadow-inner">
              <p className="text-xs font-bold text-gray-500 uppercase mb-1">Subject</p>
              <p className="text-sm font-semibold text-gray-900 mb-3">{dispatchInfo.email_subject}</p>
              <p className="text-xs font-bold text-gray-500 uppercase mb-1">Body Preview</p>
              <p className="text-sm text-gray-700 italic whitespace-pre-line">
                {dispatchInfo.email_body_preview}
              </p>
            </div>
          </motion.div>
        )}

        {/* NEW: Proactive Donor Engagement Block (Amber) */}
        {dispatchInfo && dispatchInfo.donor_engagement_sms && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="mt-4 bg-gradient-to-br from-gray-50 to-amber-50/50 border border-amber-200 rounded-xl p-5 shadow-sm"
          >
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="w-5 h-5 text-amber-600" />
              <span className="text-xs font-bold text-amber-900 uppercase tracking-wider">Proactive Agent Action</span>
              <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs font-bold rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Engagement Sent
              </span>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <p className="text-sm text-gray-700">
                Sent to <span className="font-semibold text-gray-900">{dispatchInfo.donor_engagement_sms.to}</span>
              </p>
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" /> Delivered just now
              </span>
            </div>

            <div className="bg-white p-4 rounded-lg border border-amber-100 shadow-inner">
              <p className="text-xs font-bold text-gray-500 uppercase mb-1">Automated Reply</p>
              <p className="text-sm text-gray-700 italic whitespace-pre-line">
                "{dispatchInfo.donor_engagement_sms.message}"
              </p>
            </div>
          </motion.div>
        )}

        {/* Logistics Forecast Block */}
        {logisticsInfo && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="mt-4 bg-gradient-to-br from-gray-50 to-purple-50/50 border border-purple-200 rounded-xl p-5 shadow-sm"
          >
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">Logistics Agent Insights</span>
              <span className="px-2 py-0.5 bg-purple-100 text-purple-800 text-xs font-bold rounded-full">Forecast Complete</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-xs text-gray-500 uppercase font-bold mb-1">Shortages Flagged</p>
                <ul className="list-disc list-inside text-gray-700">
                  {logisticsInfo.shortages_flagged.map((item: string, idx: number) => (
                    <li key={idx} className={item.includes("None") ? "text-green-600" : "text-red-600 font-medium"}>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-bold mb-1">Donation Impact</p>
                <p className="text-gray-700">{logisticsInfo.donation_impact}</p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    );
  }

  // PENDING STATE
  return (
    <motion.div 
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden mb-4"
    >
      {/* Header with gradient */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
            <Package className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white text-lg">Donation {donation.id}</h3>
            <p className="text-blue-100 text-xs">Ready for your review</p>
          </div>
        </div>
        <motion.span 
          animate={{ 
            boxShadow: ["0 0 0 0 rgba(253, 224, 71, 0.4)", "0 0 0 8px rgba(253, 224, 71, 0)"]
          }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="px-4 py-1.5 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full uppercase tracking-wide shadow-lg"
        >
          Awaiting Approval
        </motion.span>
      </div>

      <div className="p-6 space-y-6">
        {/* STUNNING Agent Reasoning Box */}
        <motion.div 
          variants={reasoningBoxVariants}
          initial="hidden"
          animate="visible"
          className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-blue-50/80 to-indigo-50 border border-blue-200 rounded-xl p-5"
        >
          {/* Decorative background elements */}
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-blue-200/30 rounded-full blur-2xl" />
          <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-20 h-20 bg-indigo-200/30 rounded-full blur-xl" />
          
          <div className="relative">
            <div className="flex items-start gap-4 mb-3">
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="p-2 bg-blue-100 rounded-lg"
              >
                <Sparkles className="w-5 h-5 text-blue-700" />
              </motion.div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-blue-900 mb-1 flex items-center gap-2">
                  Agent Reasoning
                  <span className="px-2 py-0.5 bg-blue-200/60 text-blue-800 text-xs rounded-full font-semibold">
                    Transparent AI
                  </span>
                </h4>
                <p className="text-xs text-blue-600/70">
                  Here's what I'm planning to do and why
                </p>
              </div>
            </div>
            
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white/70 backdrop-blur-sm border border-blue-100 rounded-lg p-4"
            >
              <p className="text-sm text-blue-900 leading-relaxed">
                I have <span className="font-semibold">parsed the incoming {donation.source || 'SMS'}</span>, 
                extracted the <span className="font-semibold">donor details</span> and 
                <span className="font-semibold"> inventory items</span>, and drafted an 
                <span className="font-semibold"> IRS-compliant receipt</span>. 
                {donation.source === 'Email' && (
                  <span className="inline-flex items-center gap-1 ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-800 text-xs rounded-full font-bold border border-indigo-200">
                    <Mail className="w-3 h-3" /> IRS Receipt Eligible
                  </span>
                )}
                This donation is ready to be added to active inventory.
              </p>
              
              {/* Visual workflow steps */}
              <div className="mt-4 flex items-center gap-2 text-xs flex-wrap">
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-100 text-green-800 rounded-md font-medium">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Parsed</span>
                </div>
                <div className="w-6 h-px bg-blue-300" />
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-100 text-green-800 rounded-md font-medium">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Extracted</span>
                </div>
                <div className="w-6 h-px bg-blue-300" />
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-100 text-green-800 rounded-md font-medium">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Drafted</span>
                </div>
                <div className="w-6 h-px bg-blue-300" />
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-100 text-yellow-800 rounded-md font-medium animate-pulse">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Awaiting You</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <motion.div 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-gray-100 rounded-lg">
              <User className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-0.5">Donor</p>
              <p className="text-gray-900 font-semibold">{donation.donor}</p>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-gray-100 rounded-lg">
              <Clock className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-0.5">Drop-off Time</p>
              <p className="text-gray-900 font-semibold">{donation.notes.replace("Dropoff at ", "")}</p>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="md:col-span-2"
          >
            <p className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-3">Items Logged</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {donation.items.map((item, idx) => (
                <motion.span 
                  key={idx}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 + (idx * 0.1) }}
                  whileHover={{ scale: 1.05, y: -2 }}
                  className="px-4 py-2 bg-gradient-to-r from-gray-50 to-gray-100 text-gray-700 text-sm font-medium rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-default"
                >
                  {item}
                </motion.span>
              ))}
            </div>
            <p className="text-xs text-gray-500">
              Total Estimated Quantity: <span className="font-bold text-gray-900 text-sm">{donation.quantity} units</span>
            </p>
          </motion.div>
        </div>

        {/* Action Buttons with animations */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex gap-4 pt-5 border-t border-gray-100"
        >
          <motion.button
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            onClick={() => handleAction("approve")}
            disabled={isProcessing}
            className="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-green-400 disabled:to-green-500 text-white font-bold py-3.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-shadow disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                <span>Approve & Log</span>
              </>
            )}
          </motion.button>
          
          <motion.button
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            onClick={() => handleAction("reject")}
            disabled={isProcessing}
            className="flex-1 bg-white hover:bg-red-50 text-red-600 border-2 border-red-200 hover:border-red-300 font-bold py-3.5 px-6 rounded-xl flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <XCircle className="w-5 h-5" />
            <span>Reject</span>
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
}