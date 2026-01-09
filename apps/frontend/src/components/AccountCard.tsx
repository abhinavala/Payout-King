import { useEffect } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import RiskStatusBadge from './RiskStatusBadge'

interface Account {
  id: string
  accountName: string
  firm: string
  accountType: string
  accountSize: number
  platform: string
}

interface AccountState {
  equity: number
  balance: number
  ruleStates: Record<string, {
    status: 'safe' | 'caution' | 'critical' | 'violated'
    remainingBuffer: number
    bufferPercent: number
    warnings: string[]
  }>
}

interface AccountCardProps {
  account: Account
  state?: AccountState
  onStateUpdate: (state: AccountState) => void
  onTest?: () => void
}

export default function AccountCard({ account, state, onStateUpdate }: AccountCardProps) {
  const { lastMessage } = useWebSocket(`/api/v1/ws/${account.id}`)

  useEffect(() => {
    if (lastMessage?.type === 'account_state_update') {
      onStateUpdate(lastMessage.data)
    }
  }, [lastMessage, onStateUpdate])

  const getRiskLevel = (): 'safe' | 'caution' | 'critical' => {
    if (!state?.ruleStates) return 'safe'
    
    const states = Object.values(state.ruleStates)
    if (states.some((s) => s.status === 'violated')) return 'critical'
    if (states.some((s) => s.status === 'critical')) return 'critical'
    if (states.some((s) => s.status === 'caution')) return 'caution'
    return 'safe'
  }

  const riskLevel = getRiskLevel()
  const riskColors = {
    safe: 'bg-green-50 border-green-200',
    caution: 'bg-amber-50 border-amber-200',
    critical: 'bg-red-50 border-red-200',
  }

  return (
    <div className={`rounded-lg border-2 p-6 ${riskColors[riskLevel]}`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{account.accountName}</h3>
          <p className="text-sm text-gray-600">
            {account.firm.charAt(0).toUpperCase() + account.firm.slice(1)} •{' '}
            {account.accountType === 'eval' ? 'Evaluation' : 
             account.accountType === 'pa' ? 'PA' : 
             account.accountType === 'funded' ? 'Funded' : account.accountType}
          </p>
        </div>
        <RiskStatusBadge status={riskLevel} size="sm" />
      </div>

      {state ? (
        <div className="space-y-3">
          <div>
            <div className="text-sm text-gray-600">Equity</div>
            <div className="text-2xl font-bold text-gray-900">
              ${state.equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>

          {Object.entries(state.ruleStates).map(([ruleName, ruleState]) => (
            <div key={ruleName} className="border-t pt-2">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {ruleName.replace(/([A-Z])/g, ' $1').trim()}
                </span>
                <span
                  className={`text-xs font-medium ${
                    ruleState.status === 'safe'
                      ? 'text-green-700'
                      : ruleState.status === 'caution'
                      ? 'text-amber-700'
                      : 'text-red-700'
                  }`}
                >
                  {ruleState.status.toUpperCase()}
                </span>
              </div>
              <div className="text-xs text-gray-600">
                Buffer: ${ruleState.remainingBuffer.toFixed(2)} ({ruleState.bufferPercent.toFixed(1)}%)
              </div>
              {ruleState.warnings.length > 0 && (
                <div className="mt-1 text-xs text-red-600">
                  {ruleState.warnings[0]}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-gray-500">No data yet</div>
      )}

      <div className="mt-4 pt-4 border-t">
        <button
          onClick={() => {
            if (onTest) onTest()
          }}
          className="w-full px-3 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          🧪 Test Account
        </button>
      </div>
    </div>
  )
}

