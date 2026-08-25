// frontend/components/DecisionCard.tsx
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Package, Mail, Phone, Calendar, Download, CheckCircle } from "lucide-react";

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

interface DecisionCardProps {
  donation: Donation;
}

export default function DecisionCard({ donation }: DecisionCardProps) {
  const [isApproved, setIsApproved] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleApprove = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/approve/${donation.id}`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.status === "success") {
        setIsApproved(true);
      }
    } catch (error) {
      console.error("Approval failed:", error);
    }
  };

  const handleDownloadReceipt = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/download-receipt/${donation.id}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tax_receipt_${donation.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-gray-200 p-6 mb-4 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Agent Reasoning Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Package className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-1">Agent Reasoning</h3>
            <p className="text-blue-800 text-sm leading-relaxed">
              I have parsed the incoming {donation.source || "donation"}, extracted the donor details and inventory items, 
              and drafted an IRS-compliant receipt. This donation is ready to be added to active inventory.
            </p>
            <div className="flex items-center gap-2 mt-3 text-xs">
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Parsed
              </span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Extracted
              </span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Drafted
              </span>
              <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full flex items-center gap-1">
                Awaiting You
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Donation Details */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
            <Package className="w-4 h-4" />
            <span className="font-semibold">DONOR</span>
          </div>
          <p className="text-gray-900 font-semibold text-lg">{donation.donor}</p>
          {donation.donor_email && (
            <p className="text-gray-600 text-sm mt-1">{donation.donor_email}</p>
          )}
          {donation.donor_phone && (
            <p className="text-gray-600 text-sm">{donation.donor_phone}</p>
          )}
        </div>
        
        <div>
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
            <Calendar className="w-4 h-4" />
            <span className="font-semibold">DROP-OFF TIME</span>
          </div>
          <p className="text-gray-900 font-semibold">{donation.notes}</p>
        </div>
      </div>

      {/* Items Logged */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
          ITEMS LOGGED
        </h3>
        <div className="flex flex-wrap gap-2">
          {donation.items.map((item, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium"
            >
              {item}
            </span>
          ))}
        </div>
        <p className="text-gray-600 text-sm mt-3">
          Total Estimated Quantity: <span className="font-semibold text-gray-900">{donation.quantity} units</span>
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        {!isApproved ? (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleApprove}
            className="flex-1 bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-6 rounded-lg font-semibold shadow-sm hover:shadow-md transition-all flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-5 h-5" />
            Approve & Log
          </motion.button>
        ) : (
          <div className="flex-1 bg-green-50 border border-green-200 text-green-800 py-3 px-6 rounded-lg font-semibold flex items-center justify-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Approved & Logged
          </div>
        )}
        
        {isApproved && (
          <motion.button
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDownloadReceipt}
            disabled={isDownloading}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg font-semibold shadow-sm hover:shadow-md transition-all disabled:opacity-50"
          >
            <Download className="w-5 h-5" />
            {isDownloading ? "Downloading..." : "Download Receipt"}
          </motion.button>
        )}
      </div>

      {/* Source Badge */}
      {donation.source && (
        <div className="mt-4 flex justify-end">
          <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            Source: {donation.source}
          </span>
        </div>
      )}
    </motion.div>
  );
}