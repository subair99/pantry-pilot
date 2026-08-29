// frontend/components/DonationHistory.tsx
"use client";

import { useState, useEffect } from "react";
import { Download, PackageCheck, Search, Inbox } from "lucide-react";
import { motion } from "framer-motion";

interface ApprovedDonation {
  id: string;
  donor_name: string;
  date: string;
  donor_email?: string;
  donor_phone?: string;
}

export default function DonationHistory() {
  const [approvedDonations, setApprovedDonations] = useState<ApprovedDonation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchApproved = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/approved-donations");
        const data = await res.json();
        setApprovedDonations(data.donations || []);
      } catch (error) {
        console.error("Failed to fetch approved donations:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApproved();
  }, []);

  // Filter donations based on search query
  const filteredDonations = approvedDonations.filter((donation) => {
    const query = searchQuery.toLowerCase();
    return (
      donation.donor_name.toLowerCase().includes(query) ||
      donation.id.toLowerCase().includes(query) ||
      donation.donor_email?.toLowerCase().includes(query) ||
      donation.donor_phone?.includes(query) ||
      donation.date.includes(query)
    );
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="mt-12 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
    >
      <div className="p-6 border-b border-gray-100 bg-gray-50">
        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <PackageCheck className="w-5 h-5 text-green-600" />
          Recently Approved Donations
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Search and re-download tax receipts for previously processed donations.
        </p>
      </div>

      {/* Search Bar - ALWAYS VISIBLE */}
      <div className="p-4 border-b border-gray-100 bg-white">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by donor name, ID, email, phone, or date..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        {searchQuery && (
          <p className="text-sm text-gray-500 mt-2">
            Found {filteredDonations.length} donation{filteredDonations.length !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      {/* Donation List or Empty State */}
      <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <p>Loading donation history...</p>
          </div>
        ) : filteredDonations.length === 0 ? (
          <div className="p-12 text-center">
            <Inbox className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            {searchQuery ? (
              <p className="text-gray-500">No donations found matching "{searchQuery}"</p>
            ) : (
              <div>
                <p className="text-gray-500 font-medium">No approved donations yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Approve a donation to see it here with a downloadable receipt.
                </p>
              </div>
            )}
          </div>
        ) : (
          filteredDonations.map((donation) => (
            <div key={donation.id} className="flex justify-between items-center p-4 hover:bg-gray-50 transition-colors">
              <div>
                <p className="font-semibold text-gray-900">{donation.donor_name}</p>
                <p className="text-sm text-gray-500">
                  ID: <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">{donation.id}</span> | Date: {donation.date}
                  {donation.donor_email && <span> | Email: {donation.donor_email}</span>}
                </p>
              </div>
              
              <a 
                href={`http://localhost:8000/api/download-receipt/${donation.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" />
                Download Receipt
              </a>
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
}