"use client";

import { Bigelow_Rules } from "next/font/google";
import { useState } from "react";

interface PendingMessage {
  filename: string;
  donor: string;
  contact: string;
  items: string | string[];
  quantity: number;
  dropoff_time: string;
  raw_message: string;
  error?: string;
}

interface ApprovedReceipt {
  filename: string;
  donor: string;
  donation_id: string;
  status: "PENDING_SEND" | "SENT";
  receipt_url?: string;
}

interface ArchivedReceipt {
  donation_id: string;
  donor: string;
  email: string;
  phone: string;
  status: string;
  date: string;
  receipt_url: string;
}

export default function Dashboard() {
  const [messages, setMessages] = useState<PendingMessage[]>([]);
  const [approvedReceipts, setApprovedReceipts] = useState<ApprovedReceipt[]>([]);
  const [archivedReceipts, setArchivedReceipts] = useState<ArchivedReceipt[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("Ready - Click Scan to begin");
  const [approvedFilenames, setApprovedFilenames] = useState<Set<string>>(new Set());

  const API_URL = process.env.NEXT_PUBLIC_API_ENDPOINT || "http://localhost:3000";

  // ✅ UPDATED: Refresh page before scanning
  const fetchMessages = async () => {
    // Refresh the page to clear any stale state
    window.location.reload();
    
    // The page will reload, so this code won't execute
    // The useEffect below will handle the scan after reload
  };

  // Scan automatically after page load (triggered by refresh)
  const scanAfterLoad = async () => {
    setIsLoading(true);
    setStatus("Scanning inbox and transcribing voice notes...");
    try {
      const res = await fetch(`${API_URL}/scan`);
      const data = await res.json();
      const unapprovedMessages = data.filter((msg: PendingMessage) => !approvedFilenames.has(msg.filename));
      setMessages(unapprovedMessages);
      setStatus(unapprovedMessages.length > 0 
        ? `${unapprovedMessages.length} new messages found!` 
        : "Inbox empty - All caught up!");
    } catch (err) {
      setStatus("Error fetching messages");
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scan on page load
  useState(() => { 
    scanAfterLoad(); 
  });

  const handleApprove = async (msg: PendingMessage) => {
    if (approvedFilenames.has(msg.filename) || isLoading) return;
    setIsLoading(true);
    setStatus(`Approving ${msg.filename}...`);
    try {
      const res = await fetch(`${API_URL}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: msg.filename, parsed_data: msg }),
      });
      const data = await res.json();
      setApprovedFilenames(prev => new Set(prev).add(msg.filename));
      const donationId = data.donation_id || `DON-${Math.floor(Math.random() * 9000) + 1000}`;
      setApprovedReceipts(prev => [...prev, { 
        filename: msg.filename, 
        donor: msg.donor, 
        donation_id: donationId, 
        status: "PENDING_SEND",
        receipt_url: data.receipt_url 
      }]);
      setMessages((prev) => prev.filter((m) => m.filename !== msg.filename));
      setStatus(`Approved! Receipt ${donationId} generated.`);
    } catch (err) {
      setStatus("Error approving message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendReceipt = async (donationId: string, email?: string) => {
    setStatus(`Sending receipt ${donationId}...`);
    try {
      const res = await fetch(`${API_URL}/send-receipt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ donation_id: donationId }),
      });
      const data = await res.json();
      if (data.error) setStatus(`Error: ${data.error}`);
      else {
        setStatus(`Receipt ${donationId} sent to ${email || 'donor'} successfully!`);
        setApprovedReceipts(prev => prev.map(r => r.donation_id === donationId ? { ...r, status: "SENT" } : r));
      }
    } catch (err) {
      setStatus("Error sending receipt");
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setArchivedReceipts([]);
      return;
    }
    setIsLoading(true);
    setStatus(`Searching archive for "${searchQuery}"...`);
    try {
      const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setArchivedReceipts(data);
      setStatus(`Found ${data.length} records in archive.`);
    } catch (err) {
      setStatus("Error searching archive");
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ Limit recent approvals to max 3 items
  const recentApprovals = approvedReceipts.slice(-3).reverse();

  return (
    <main className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        
        {/* HEADER with Scan button */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900"> PantryPilot</h1>
            <p className="text-sm md:text-base text-gray-600 mt-1">Approval Pipeline</p>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={fetchMessages} 
              disabled={isLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition flex items-center gap-2"
            >
              {isLoading ? 'Refreshing...' : ' Scan Inbox'}
            </button>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-lg mb-6 flex items-center gap-2 text-sm">
          <span className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-500'}`}></span>
          Status: {status}
        </div>

        {/* PENDING APPROVALS */}
        <h2 className="text-lg md:text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          📥 Pending
          <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded-full">{messages.length}</span>
        </h2>
        <div className="grid gap-3 mb-8">
          {messages.length === 0 && !isLoading && (
            <div className="text-center py-6 bg-white rounded-lg border border-gray-200 border-dashed">
              <p className="text-gray-500">Click "Scan Inbox" to check for new messages</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded mb-2">
                    {msg.filename.includes('voice') ? '🎙️ Voice' : msg.filename.includes('sms') ? '📱 SMS' : '📧 Email'}
                  </span>
                  <h3 className="text-base font-bold text-gray-900">{msg.donor || "Unknown Donor"}</h3>
                  <p className="text-xs text-gray-500">{msg.contact}</p>
                </div>
                <button onClick={() => handleApprove(msg)} disabled={isLoading} className="bg-green-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition">
                  ✅ Approve
                </button>
              </div>
              <div className="bg-gray-50 p-2 rounded border border-gray-100">
                <p className="text-gray-700 text-xs italic">"{msg.raw_message}"</p>
              </div>
            </div>
          ))}
        </div>

        {/* RECENT APPROVALS (MAX 3) */}
        {recentApprovals.length > 0 && (
          <>
            <h2 className="text-lg md:text-xl font-bold text-gray-800 mb-4">
               Recent (Last 3)
            </h2>
            <div className="grid gap-3 mb-8">
              {recentApprovals.map((receipt, idx) => (
                <div key={`${receipt.filename}-${idx}`} className={`bg-white rounded-lg border shadow-sm p-4 ${receipt.status === "SENT" ? "border-green-200 bg-green-50" : "border-yellow-200 bg-yellow-50"}`}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs font-bold text-gray-700 bg-gray-200 px-2 py-0.5 rounded">{receipt.donation_id}</span>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${receipt.status === "SENT" ? "bg-green-200 text-green-800" : "bg-yellow-200 text-yellow-800"}`}>
                          {receipt.status === "SENT" ? "✅ SENT" : " PENDING"}
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-gray-900">{receipt.donor}</h3>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <a 
                      href={receipt.receipt_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex-1 bg-blue-600 text-white text-center px-3 py-1.5 rounded text-xs font-medium hover:bg-blue-700 transition"
                    >
                       View PDF
                    </a>
                    <button 
                      onClick={() => handleSendReceipt(receipt.donation_id)} 
                      disabled={isLoading || receipt.status === "SENT"} 
                      className={`flex-1 px-3 py-1.5 rounded text-xs font-medium transition ${receipt.status === "SENT" ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}
                    >
                      {receipt.status === "SENT" ? "✅ Sent" : " Send Email"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* SEARCH ARCHIVE */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 mb-8">
          <h2 className="text-lg md:text-xl font-bold text-gray-800 mb-4">
            🔍 Search Archive
          </h2>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Name, phone, or email..."
              className="flex-1 border border-gray-300 bg-white text-gray-900 placeholder:text-gray-400 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} disabled={isLoading} className="bg-gray-800 text-white px-4 py-2 rounded text-sm font-medium hover:bg-gray-900 disabled:opacity-50 transition">
              Search
            </button>
          </div>

          {archivedReceipts.length > 0 && (
            <div className="grid gap-2">
              {archivedReceipts.map((item, idx) => (
                <div key={idx} className="bg-gray-50 rounded p-3 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-gray-700 bg-white px-2 py-0.5 rounded border">{item.donation_id}</span>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${item.status === 'SENT_TO_DONOR' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'}`}>
                      {item.status === 'SENT_TO_DONOR' ? '✅ SENT' : ' PENDING'}
                    </span>
                  </div>
                  <h4 className="font-bold text-gray-900 text-sm mb-1">{item.donor}</h4>
                  <p className="text-xs text-gray-500 mb-2">📧 {item.email} | 📱 {item.phone}</p>
                  <div className="flex gap-2">
                    <a 
                      href={item.receipt_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex-1 bg-blue-600 text-white text-center px-3 py-1.5 rounded text-xs font-medium hover:bg-blue-700 transition"
                    >
                       View PDF
                    </a>
                    <button 
                      onClick={() => handleSendReceipt(item.donation_id, item.email)}
                      disabled={isLoading || item.status === 'SENT_TO_DONOR'}
                      className={`flex-1 px-3 py-1.5 rounded text-xs font-medium transition ${item.status === 'SENT_TO_DONOR' ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}
                    >
                      {item.status === 'SENT_TO_DONOR' ? '✅ Sent' : '📧 Send Email'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          {archivedReceipts.length === 0 && searchQuery && !isLoading && (
            <p className="text-center text-gray-500 py-4 text-sm">No records found</p>
          )}
        </div>

      </div>
    </main>
  );
}