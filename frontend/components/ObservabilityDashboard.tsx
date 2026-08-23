// frontend/components/ObservabilityDashboard.tsx
"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Clock, CheckCircle, AlertCircle, TrendingUp } from "lucide-react";

interface Trace {
  trace_id: string;
  operation: string;
  agent: string;
  duration_ms: string;
  status: string;
  timestamp: string;
}

interface Metrics {
  total_requests: number;
  success_rate: string;
  average_latencies_ms: Record<string, number>;
}

export default function ObservabilityDashboard() {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tracesRes, metricsRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/traces"),
          fetch("http://127.0.0.1:8000/api/metrics")
        ]);
        const tracesData = await tracesRes.json();
        const metricsData = await metricsRes.json();
        setTraces(tracesData.traces || []);
        setMetrics(metricsData.metrics || null);
      } catch (error) {
        console.error("Failed to fetch observability data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000); // Refresh every 3 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6 mt-8">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-900">System Observability</h2>
      </div>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5 border border-blue-200"
          >
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-semibold text-blue-900">Total Requests</span>
            </div>
            <p className="text-3xl font-bold text-blue-900">{metrics.total_requests}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5 border border-green-200"
          >
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-semibold text-green-900">Success Rate</span>
            </div>
            <p className="text-3xl font-bold text-green-900">{metrics.success_rate}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5 border border-purple-200"
          >
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-semibold text-purple-900">Avg Latency</span>
            </div>
            <p className="text-3xl font-bold text-purple-900">
              {Object.values(metrics.average_latencies_ms)[0]?.toFixed(0) || 0}ms
            </p>
          </motion.div>
        </div>
      )}

      {/* Recent Traces */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Agent Traces</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {traces.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No traces yet. Trigger a donation to see agent activity.</p>
          ) : (
            traces.map((trace, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-200"
              >
                <div className="flex items-center gap-3">
                  {trace.status === "success" ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{trace.operation}</p>
                    <p className="text-xs text-gray-500">{trace.agent} • {trace.timestamp}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-mono text-gray-700">{trace.duration_ms}ms</p>
                  <p className="text-xs text-gray-500">ID: {trace.trace_id}</p>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}