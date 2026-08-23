// frontend/components/AgentLog.tsx
"use client";

import { motion } from "framer-motion";
import { Bot, Shield, CheckCircle, AlertTriangle, Send, Package, Activity, Clock } from "lucide-react";

interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  action?: string;
  details?: any;
}

interface AgentLogProps {
  logs: LogEntry[];
}

// Helper to determine icon and color based on the agent/logger name
const getAgentStyle = (logger: string) => {
  if (logger.includes("Orchestrator")) return { icon: Activity, color: "text-purple-600", bg: "bg-purple-100", border: "border-purple-200" };
  if (logger.includes("Intake")) return { icon: Package, color: "text-blue-600", bg: "bg-blue-100", border: "border-blue-200" };
  if (logger.includes("Dispatch")) return { icon: Send, color: "text-green-600", bg: "bg-green-100", border: "border-green-200" };
  if (logger.includes("Logistics")) return { icon: Bot, color: "text-indigo-600", bg: "bg-indigo-100", border: "border-indigo-200" };
  if (logger.includes("Guardrails")) return { icon: Shield, color: "text-red-600", bg: "bg-red-100", border: "border-red-200" };
  return { icon: Bot, color: "text-gray-600", bg: "bg-gray-100", border: "border-gray-200" };
};

export default function AgentLog({ logs }: AgentLogProps) {
  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center shadow-sm">
        <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 font-medium">No agent activity recorded yet.</p>
        <p className="text-gray-400 text-sm mt-1">Trigger a donation to see the reasoning engine in action.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white rounded-lg shadow-sm border border-gray-200">
            <Activity className="w-5 h-5 text-gray-700" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg">Agent Activity Log</h3>
            <p className="text-xs text-gray-500">Transparent Reasoning Engine</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full">
          {logs.length} Events
        </span>
      </div>

      {/* Timeline Container */}
      <div className="p-6 max-h-[500px] overflow-y-auto space-y-4 custom-scrollbar">
        {logs.map((log, index) => {
          const style = getAgentStyle(log.logger);
          const Icon = style.icon;
          const time = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className="relative pl-8"
            >
              {/* Vertical connecting line */}
              {index < logs.length - 1 && (
                <div className="absolute left-[11px] top-6 bottom-[-16px] w-0.5 bg-gray-200" />
              )}
              
              {/* Timeline Dot */}
              <div className={`absolute left-0 top-1.5 w-6 h-6 rounded-full ${style.bg} border-2 border-white shadow-sm flex items-center justify-center z-10`}>
                <Icon className={`w-3.5 h-3.5 ${style.color}`} />
              </div>

              {/* Content Card */}
              <div className={`bg-gray-50/50 border ${style.border} rounded-xl p-4 hover:shadow-md transition-shadow`}>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold uppercase tracking-wider ${style.color}`}>
                      {log.logger.split('.').pop()}
                    </span>
                    {log.level === "WARNING" || log.level === "ERROR" ? (
                      <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-[10px] font-bold rounded-full flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> {log.level}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-green-100 text-green-800 text-[10px] font-bold rounded-full flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> {log.level}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-gray-400 font-mono flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {time}
                  </span>
                </div>
                
                <p className="text-sm text-gray-800 font-medium mb-2">{log.message}</p>
                
                {/* Action & Details (Expandable look) */}
                {log.action && (
                  <div className="bg-white rounded-lg p-3 border border-gray-200 text-xs">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-500 font-semibold uppercase">Action:</span>
                      <span className="font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded">{log.action}</span>
                    </div>
                    {log.details && (
                      <pre className="text-gray-600 font-mono mt-2 whitespace-pre-wrap overflow-x-auto text-[11px]">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}