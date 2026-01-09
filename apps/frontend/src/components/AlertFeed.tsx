/**
 * AlertFeed Component
 * 
 * Real-time alert feed showing rule violations and status changes.
 * Per Master Plan: View 5 - Alert feed
 * 
 * Frontend never computes - all alerts from backend.
 */

interface Alert {
  id: string
  accountId: string
  accountName: string
  ruleName: string
  message: string
  severity: 'info' | 'warning' | 'critical' | 'violated'
  timestamp: string
}

interface AlertFeedProps {
  alerts: Alert[]
  maxAlerts?: number
}

export default function AlertFeed({ alerts, maxAlerts = 50 }: AlertFeedProps) {
  const displayAlerts = alerts.slice(0, maxAlerts)

  const severityColors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    critical: 'bg-red-50 border-red-200 text-red-800',
    violated: 'bg-red-100 border-red-300 text-red-900',
  }

  const severityIcons = {
    info: 'ℹ️',
    warning: '⚠️',
    critical: '🔴',
    violated: '❌',
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleString()
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Feed</h3>

      {displayAlerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No alerts yet</p>
          <p className="text-xs mt-2">Alerts will appear here when rule states change</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`border rounded-lg p-3 ${severityColors[alert.severity]}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span>{severityIcons[alert.severity]}</span>
                    <span className="font-medium">{alert.accountName}</span>
                    <span className="text-xs opacity-75">
                      {alert.ruleName.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </div>
                  <p className="text-sm">{alert.message}</p>
                </div>
                <span className="text-xs opacity-75 ml-4 whitespace-nowrap">
                  {formatTimestamp(alert.timestamp)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
