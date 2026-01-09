import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getAccounts } from '../services/api'
import AccountCard from '../components/AccountCard'
import ConnectAccountModal from '../components/ConnectAccountModal'
import TestAccountModal from '../components/TestAccountModal'
import MultiAccountTable from '../components/MultiAccountTable'
import AlertFeed from '../components/AlertFeed'
import Disclaimer from '../components/Disclaimer'
import { useWebSocket } from '../hooks/useWebSocket'

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
  ruleStates: Record<string, any>
  overallRiskLevel?: 'safe' | 'caution' | 'critical' | 'violated'
  lastUpdate?: string
}

interface Alert {
  id: string
  accountId: string
  accountName: string
  ruleName: string
  message: string
  severity: 'info' | 'warning' | 'critical' | 'violated'
  timestamp: string
}

export default function Dashboard() {
  const { user, token } = useAuth()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [accountStates, setAccountStates] = useState<Record<string, AccountState>>({})
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showConnectModal, setShowConnectModal] = useState(false)
  const [testAccount, setTestAccount] = useState<Account | null>(null)
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table')

  useEffect(() => {
    if (token) {
      loadAccounts()
    }
  }, [token])

  const loadAccounts = async () => {
    try {
      const accountsData = await getAccounts(token!)
      setAccounts(accountsData)
      
      // Connect WebSocket for each account
      accountsData.forEach((account: Account) => {
        // WebSocket connection will be handled by useWebSocket hook
      })
    } catch (error) {
      console.error('Failed to load accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAccountStateUpdate = (accountId: string, state: AccountState) => {
    setAccountStates((prev) => {
      const prevState = prev[accountId]
      const newState = { ...state, lastUpdate: new Date().toISOString() }

      // Generate alerts for status changes
      if (prevState) {
        Object.entries(state.ruleStates || {}).forEach(([ruleName, ruleState]: [string, any]) => {
          const prevRuleState = prevState.ruleStates?.[ruleName]
          if (prevRuleState && prevRuleState.status !== ruleState.status) {
            const account = accounts.find((a) => a.id === accountId)
            const severity =
              ruleState.status === 'violated'
                ? 'violated'
                : ruleState.status === 'critical'
                ? 'critical'
                : ruleState.status === 'caution'
                ? 'warning'
                : 'info'

            const alert: Alert = {
              id: `${accountId}-${ruleName}-${Date.now()}`,
              accountId,
              accountName: account?.accountName || accountId,
              ruleName,
              message: ruleState.warnings?.[0] || `${ruleName} status changed to ${ruleState.status}`,
              severity,
              timestamp: new Date().toISOString(),
            }

            setAlerts((prevAlerts) => [alert, ...prevAlerts].slice(0, 100))
          }
        })
      }

      return {
        ...prev,
        [accountId]: newState,
      }
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading accounts...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Payout King</h1>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-700">{user?.email}</span>
              <button
                onClick={() => {
                  // TODO: Implement logout
                }}
                className="ml-4 text-sm text-indigo-600 hover:text-indigo-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <Disclaimer variant="compact" />
          
          <div className="flex justify-between items-center mb-6 mt-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Accounts</h2>
            <div className="flex gap-2">
              {accounts.length > 0 && (
                <>
                  <button
                    onClick={() => setViewMode(viewMode === 'table' ? 'cards' : 'table')}
                    className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    {viewMode === 'table' ? '📋 Cards' : '📊 Table'}
                  </button>
                  <button
                    onClick={() => setShowConnectModal(true)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    + Connect Account
                  </button>
                </>
              )}
            </div>
          </div>

          {accounts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No accounts connected yet.</p>
              <button
                onClick={() => setShowConnectModal(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Connect Account
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main content area */}
              <div className={viewMode === 'table' ? 'lg:col-span-2' : 'lg:col-span-3'}>
                {viewMode === 'table' ? (
                  <MultiAccountTable
                    accounts={accounts}
                    accountStates={accountStates}
                    onAccountClick={(accountId) => {
                      const account = accounts.find((a) => a.id === accountId)
                      if (account) setTestAccount(account)
                    }}
                  />
                ) : (
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {accounts.map((account) => (
                      <AccountCard
                        key={account.id}
                        account={account}
                        state={accountStates[account.id]}
                        onStateUpdate={(state) => handleAccountStateUpdate(account.id, state)}
                        onTest={() => setTestAccount(account)}
                      />
                    ))}
                  </div>
                )}
              </div>

              {/* Alert feed sidebar */}
              {viewMode === 'table' && (
                <div className="lg:col-span-1">
                  <AlertFeed alerts={alerts} />
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <ConnectAccountModal
        isOpen={showConnectModal}
        onClose={() => setShowConnectModal(false)}
        onSuccess={() => {
          loadAccounts()
          setShowConnectModal(false)
        }}
      />

      {testAccount && (
        <TestAccountModal
          isOpen={!!testAccount}
          onClose={() => setTestAccount(null)}
          accountId={testAccount.id}
          accountName={testAccount.accountName}
          firm={testAccount.firm}
          onUpdate={() => {
            loadAccounts()
            setTestAccount(null)
          }}
        />
      )}
    </div>
  )
}

