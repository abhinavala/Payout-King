import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

interface TestAccountModalProps {
  isOpen: boolean
  onClose: () => void
  accountId: string
  accountName: string
  firm: string
  onUpdate: () => void
}

interface Scenario {
  id: string
  name: string
  description: string
}

interface RuleState {
  status: string
  remaining_buffer: number
  buffer_percent: number
  recoverable: string
  severity: string
  warnings: string[]
  recovery_path: string | null
}

export default function TestAccountModal({
  isOpen,
  onClose,
  accountId,
  accountName,
  firm,
  onUpdate,
}: TestAccountModalProps) {
  const { token } = useAuth()
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [selectedScenario, setSelectedScenario] = useState('normal')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadScenarios()
    }
  }, [isOpen])

  const loadScenarios = async () => {
    try {
      const response = await fetch('/api/v1/test/test-scenarios')
      const data = await response.json()
      setScenarios(data.scenarios)
    } catch (err) {
      console.error('Failed to load scenarios:', err)
    }
  }

  const handleTest = async () => {
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(
        `/api/v1/test/simulate-account-data/${accountId}?scenario=${selectedScenario}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Test failed')
      }

      const data = await response.json()
      setResult(data)
      onUpdate() // Refresh dashboard
    } catch (err: any) {
      setError(err.message || 'Failed to run test')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':
        return 'text-green-600 bg-green-50'
      case 'caution':
        return 'text-yellow-600 bg-yellow-50'
      case 'critical':
        return 'text-orange-600 bg-orange-50'
      case 'violated':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getRecoverableBadge = (recoverable: boolean | string) => {
    const recoverableStr = typeof recoverable === 'boolean' 
      ? (recoverable ? 'recoverable' : 'non_recoverable')
      : recoverable
    
    if (recoverableStr === 'non_recoverable' || recoverableStr === false) {
      return <span className="text-red-600 font-semibold">❌ Non-Recoverable</span>
    } else if (recoverableStr === 'recoverable' || recoverableStr === true) {
      return <span className="text-green-600 font-semibold">✅ Recoverable</span>
    }
    return <span className="text-yellow-600 font-semibold">⚠️ Sometimes</span>
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Test Account: {accountName}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          {/* Scenario Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Scenario
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {scenarios.map((scenario) => (
                <option key={scenario.id} value={scenario.id}>
                  {scenario.name} - {scenario.description}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleTest}
            disabled={loading}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Running Test...' : 'Run Test Scenario'}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4 mt-4">
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">Account State</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Equity:</span> ${result.account_state.equity.toLocaleString()}
                  </div>
                  <div>
                    <span className="font-medium">Balance:</span> ${result.account_state.balance.toLocaleString()}
                  </div>
                  <div>
                    <span className="font-medium">Daily PnL:</span>{' '}
                    <span className={result.account_state.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      ${result.account_state.daily_pnl.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium">Unrealized PnL:</span>{' '}
                    <span className={result.account_state.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      ${result.account_state.unrealized_pnl.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">
                  Overall Risk Level:{' '}
                  <span className={getStatusColor(result.overall_risk_level)}>
                    {result.overall_risk_level.toUpperCase()}
                  </span>
                </h3>
              </div>

              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">Rule States</h3>
                <div className="space-y-3">
                  {Object.entries(result.rule_states).map(([ruleName, ruleState]: [string, any]) => (
                    <div
                      key={ruleName}
                      className={`p-4 rounded-lg border ${getStatusColor(ruleState.status)}`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold capitalize">
                          {ruleName.replace(/_/g, ' ')}
                        </h4>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(ruleState.status)}`}>
                          {ruleState.status.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="text-sm space-y-1">
                        <div>
                          <span className="font-medium">Remaining Buffer:</span> $
                          {ruleState.remaining_buffer.toLocaleString()} ({ruleState.buffer_percent.toFixed(1)}%)
                        </div>
                        <div>
                          <span className="font-medium">Recoverable:</span> {getRecoverableBadge(ruleState.recoverable)}
                        </div>
                        <div>
                          <span className="font-medium">Severity:</span> {ruleState.severity.replace(/_/g, ' ')}
                        </div>
                        {ruleState.warnings && ruleState.warnings.length > 0 && (
                          <div className="mt-2">
                            <span className="font-medium">Warnings:</span>
                            <ul className="list-disc list-inside ml-2">
                              {ruleState.warnings.map((warning: string, idx: number) => (
                                <li key={idx}>{warning}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {ruleState.recovery_path && (
                          <div className="mt-2 p-2 bg-blue-50 rounded">
                            <span className="font-medium">Recovery Path:</span> {ruleState.recovery_path}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {result.max_allowed_risk && Object.keys(result.max_allowed_risk).length > 0 && (
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold mb-2">Safe Limits</h3>
                  <div className="text-sm space-y-1">
                    {Object.entries(result.max_allowed_risk).map(([key, value]: [string, any]) => (
                      <div key={key}>
                        <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span> $
                        {value.toLocaleString()}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

