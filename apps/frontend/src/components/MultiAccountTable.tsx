/**
 * MultiAccountTable Component
 * 
 * Main dashboard table showing all accounts with risk status.
 * Per Master Plan: View 1 - Multi-account table
 * 
 * Frontend never computes rules - all data from backend.
 */

import { useState } from 'react'
import RiskStatusBadge from './RiskStatusBadge'
import RuleBreakdownPanel from './RuleBreakdownPanel'

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
  overallRiskLevel?: 'safe' | 'caution' | 'critical' | 'violated'
  lastUpdate?: string
}

interface MultiAccountTableProps {
  accounts: Account[]
  accountStates: Record<string, AccountState>
  onAccountClick?: (accountId: string) => void
}

export default function MultiAccountTable({
  accounts,
  accountStates,
  onAccountClick,
}: MultiAccountTableProps) {
  const [expandedAccount, setExpandedAccount] = useState<string | null>(null)

  const getOverallRiskLevel = (accountId: string): 'safe' | 'caution' | 'critical' | 'violated' | 'disconnected' => {
    const state = accountStates[accountId]
    if (!state) return 'disconnected'
    if (state.overallRiskLevel) return state.overallRiskLevel

    // Fallback: determine from rule states
    const states = Object.values(state.ruleStates || {})
    if (states.some((s) => s.status === 'violated')) return 'violated'
    if (states.some((s) => s.status === 'critical')) return 'critical'
    if (states.some((s) => s.status === 'caution')) return 'caution'
    return 'safe'
  }

  const formatAccountType = (type: string) => {
    if (type === 'eval') return 'Evaluation'
    if (type === 'pa') return 'PA'
    if (type === 'funded') return 'Funded'
    return type
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Account
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Firm / Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Equity
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {accounts.map((account) => {
            const state = accountStates[account.id]
            const riskLevel = getOverallRiskLevel(account.id)
            const isExpanded = expandedAccount === account.id

            return (
              <>
                <tr
                  key={account.id}
                  className={`hover:bg-gray-50 cursor-pointer ${
                    riskLevel === 'violated' ? 'bg-red-50' : riskLevel === 'critical' ? 'bg-red-50' : ''
                  }`}
                  onClick={() => setExpandedAccount(isExpanded ? null : account.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{account.accountName}</div>
                    <div className="text-xs text-gray-500">{account.platform}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {account.firm.charAt(0).toUpperCase() + account.firm.slice(1)}
                    </div>
                    <div className="text-xs text-gray-500">{formatAccountType(account.accountType)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {state ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          ${state.equity.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </div>
                        <div className="text-xs text-gray-500">
                          Balance: ${state.balance.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </div>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-400">No data</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <RiskStatusBadge status={riskLevel} size="sm" />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (onAccountClick) onAccountClick(account.id)
                      }}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
                {isExpanded && state && (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 bg-gray-50">
                      <RuleBreakdownPanel
                        accountName={account.accountName}
                        ruleStates={state.ruleStates}
                        overallRiskLevel={riskLevel}
                      />
                    </td>
                  </tr>
                )}
              </>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
