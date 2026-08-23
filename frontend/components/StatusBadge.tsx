// frontend/components/StatusBadge.tsx
"use client";

import { motion } from "framer-motion";
import { Loader2, CheckCircle2, AlertCircle, Moon, Clock, Sparkles } from "lucide-react";

// Define the possible states of the agent
export type AgentStatus = "idle" | "thinking" | "awaiting_approval" | "success" | "error";

interface StatusBadgeProps {
  status: AgentStatus;
  customText?: string;
}

// Configuration for each state's visual style
const statusConfig = {
  idle: {
    text: "System Idle",
    icon: Moon,
    bg: "bg-gray-100",
    textCol: "text-gray-600",
    border: "border-gray-200",
    dot: "bg-gray-400",
  },
  thinking: {
    text: "Agent Thinking...",
    icon: Sparkles,
    bg: "bg-blue-50",
    textCol: "text-blue-700",
    border: "border-blue-200",
    dot: "bg-blue-500",
  },
  awaiting_approval: {
    text: "Awaiting Human Approval",
    icon: Clock,
    bg: "bg-yellow-50",
    textCol: "text-yellow-800",
    border: "border-yellow-200",
    dot: "bg-yellow-500",
  },
  success: {
    text: "Action Approved",
    icon: CheckCircle2,
    bg: "bg-green-50",
    textCol: "text-green-700",
    border: "border-green-200",
    dot: "bg-green-500",
  },
  error: {
    text: "Action Failed",
    icon: AlertCircle,
    bg: "bg-red-50",
    textCol: "text-red-700",
    border: "border-red-200",
    dot: "bg-red-500",
  },
};

export default function StatusBadge({ status, customText }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;
  const displayText = customText || config.text;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
      className={`inline-flex items-center gap-2.5 px-4 py-2 rounded-full border ${config.bg} ${config.border} shadow-sm`}
    >
      {/* Animated Status Dot */}
      <div className="relative flex items-center justify-center">
        <div className={`w-2 h-2 rounded-full ${config.dot}`} />
        {status === "thinking" && (
          <motion.div
            className={`absolute w-2 h-2 rounded-full ${config.dot}`}
            animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut" }}
          />
        )}
        {status === "awaiting_approval" && (
          <motion.div
            className={`absolute w-2 h-2 rounded-full ${config.dot}`}
            animate={{ scale: [1, 2], opacity: [0.5, 0] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeOut" }}
          />
        )}
      </div>

      {/* Icon */}
      {status === "thinking" ? (
        <Loader2 className={`w-4 h-4 ${config.textCol} animate-spin`} />
      ) : (
        <Icon className={`w-4 h-4 ${config.textCol}`} />
      )}

      {/* Text */}
      <span className={`text-xs font-bold uppercase tracking-wider ${config.textCol}`}>
        {displayText}
      </span>
    </motion.div>
  );
}