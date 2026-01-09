/**
 * DistanceToViolation Component
 * 
 * Displays distance-to-violation metrics with visual progress bars.
 * Frontend never computes - all values come from backend.
 */

interface DistanceToViolationProps {
  ruleName: string
  remainingBuffer: number
  bufferPercent: number
  status: 'safe' | 'caution' | 'critical' | 'violated'
  unit?: 'dollars' | 'contracts' | 'percentage'
}

export default function DistanceToViolation({
  ruleName,
  remainingBuffer,
  bufferPercent,
  status,
  unit = 'dollars',
}: DistanceToViolationProps) {
  // Color coding per Master Plan
  const barColors = {
    safe: 'bg-green-500',
    caution: 'bg-yellow-500',
    critical: 'bg-red-500',
    violated: 'bg-red-600',
  }

  const formatValue = (value: number) => {
    if (unit === 'dollars') {
      return `$${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    } else if (unit === 'contracts') {
      return `${Math.abs(value)} contracts`
    } else {
      return `${Math.abs(value).toFixed(1)}%`
    }
  }

  const displayName = ruleName
    .replace(/([A-Z])/g, ' $1')
    .trim()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">{displayName}</span>
        <span
          className={`text-xs font-medium ${
            status === 'safe'
              ? 'text-green-700'
              : status === 'caution'
              ? 'text-yellow-700'
              : 'text-red-700'
          }`}
        >
          {status.toUpperCase()}
        </span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full transition-all ${barColors[status]}`}
          style={{ width: `${Math.max(0, Math.min(100, bufferPercent))}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-gray-600">
        <span>
          {remainingBuffer >= 0 ? (
            <>Remaining: {formatValue(remainingBuffer)}</>
          ) : (
            <>Exceeded by: {formatValue(remainingBuffer)}</>
          )}
        </span>
        <span>{bufferPercent.toFixed(1)}% buffer</span>
      </div>
    </div>
  )
}
