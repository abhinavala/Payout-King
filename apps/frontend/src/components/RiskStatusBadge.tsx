/**
 * RiskStatusBadge Component
 * 
 * Displays risk status with strict color coding per Master Plan:
 * - Green: safe
 * - Yellow: approaching (caution)
 * - Red: imminent (critical/violated)
 * - Gray: disconnected
 * 
 * Frontend never computes rules - status comes from backend.
 */

interface RiskStatusBadgeProps {
  status: 'safe' | 'caution' | 'critical' | 'violated' | 'disconnected'
  size?: 'sm' | 'md' | 'lg'
}

export default function RiskStatusBadge({ status, size = 'md' }: RiskStatusBadgeProps) {
  const colorClasses = {
    safe: 'bg-green-100 text-green-800 border-green-300',
    caution: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    critical: 'bg-red-100 text-red-800 border-red-300',
    violated: 'bg-red-100 text-red-800 border-red-300',
    disconnected: 'bg-gray-100 text-gray-800 border-gray-300',
  }

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  const statusLabels = {
    safe: 'SAFE',
    caution: 'CAUTION',
    critical: 'CRITICAL',
    violated: 'VIOLATED',
    disconnected: 'DISCONNECTED',
  }

  return (
    <span
      className={`inline-flex items-center font-medium rounded border ${colorClasses[status]} ${sizeClasses[size]}`}
    >
      {statusLabels[status]}
    </span>
  )
}
