/**
 * RuleBreakdownPanel Component
 * 
 * Shows detailed rule breakdown for an account.
 * Frontend never computes rules - all data from backend.
 */

import RiskStatusBadge from './RiskStatusBadge'
import DistanceToViolation from './DistanceToViolation'
import Disclaimer from './Disclaimer'

interface RuleState {
  status: 'safe' | 'caution' | 'critical' | 'violated'
  remainingBuffer: number
  bufferPercent: number
  currentValue: number
  threshold: number
  warnings: string[]
  distanceToViolation: {
    dollars?: number
    contracts?: number
    percent?: number
  }
}

interface RuleBreakdownPanelProps {
  accountName: string
  ruleStates: Record<string, RuleState>
  overallRiskLevel: 'safe' | 'caution' | 'critical' | 'violated'
}

export default function RuleBreakdownPanel({
  accountName,
  ruleStates,
  overallRiskLevel,
}: RuleBreakdownPanelProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{accountName}</h3>
        <RiskStatusBadge status={overallRiskLevel} />
      </div>
      
      <div className="mb-4">
        <Disclaimer variant="inline" />
      </div>

      <div className="space-y-4">
        {Object.entries(ruleStates).map(([ruleName, ruleState]) => {
          // Determine unit based on rule type
          let unit: 'dollars' | 'contracts' | 'percentage' = 'dollars'
          if (ruleName.includes('position')) {
            unit = 'contracts'
          } else if (ruleName.includes('consistency')) {
            unit = 'percentage'
          }

          return (
            <div key={ruleName} className="border-t pt-4 first:border-t-0 first:pt-0">
              <DistanceToViolation
                ruleName={ruleName}
                remainingBuffer={ruleState.remainingBuffer}
                bufferPercent={ruleState.bufferPercent}
                status={ruleState.status}
                unit={unit}
              />

              {ruleState.warnings.length > 0 && (
                <div className="mt-2">
                  {ruleState.warnings.map((warning, idx) => (
                    <div
                      key={idx}
                      className={`text-xs p-2 rounded ${
                        ruleState.status === 'violated'
                          ? 'bg-red-50 text-red-800'
                          : ruleState.status === 'critical'
                          ? 'bg-red-50 text-red-700'
                          : 'bg-yellow-50 text-yellow-700'
                      }`}
                    >
                      ⚠️ {warning}
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-2 text-xs text-gray-500 grid grid-cols-2 gap-2">
                <div>
                  <span className="font-medium">Current:</span>{' '}
                  {typeof ruleState.currentValue === 'number'
                    ? ruleState.currentValue.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })
                    : ruleState.currentValue}
                </div>
                <div>
                  <span className="font-medium">Threshold:</span>{' '}
                  {typeof ruleState.threshold === 'number'
                    ? ruleState.threshold.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })
                    : ruleState.threshold}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
