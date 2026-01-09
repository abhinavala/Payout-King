import { useState, useEffect } from 'react'
import { createAccount } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

interface Firm {
  id: string
  display_name: string
  description: string
  rules_summary: Record<string, string>
}

interface AccountType {
  id: string
  display_name: string
  description: string
}

interface ConnectAccountModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function ConnectAccountModal({
  isOpen,
  onClose,
  onSuccess,
}: ConnectAccountModalProps) {
  const { token } = useAuth()
  const [firms, setFirms] = useState<Firm[]>([])
  const [accountTypes, setAccountTypes] = useState<AccountType[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Form state
  const [platform, setPlatform] = useState('ninjatrader')
  const [selectedFirm, setSelectedFirm] = useState('apex')
  const [selectedAccountType, setSelectedAccountType] = useState('eval')
  const [accountId, setAccountId] = useState('')
  const [accountName, setAccountName] = useState('')
  const [accountSize, setAccountSize] = useState(50000)
  const [selectedFirmRules, setSelectedFirmRules] = useState<any>(null)

  useEffect(() => {
    if (isOpen) {
      loadFirms()
      loadAccountTypes()
    }
  }, [isOpen])

  useEffect(() => {
    if (selectedFirm) {
      loadFirmRules(selectedFirm, selectedAccountType)
    }
  }, [selectedFirm, selectedAccountType])

  const loadFirms = async () => {
    try {
      const response = await fetch('/api/v1/firms/')
      const data = await response.json()
      setFirms(data.firms)
    } catch (err) {
      console.error('Failed to load firms:', err)
    }
  }

  const loadAccountTypes = async () => {
    try {
      const response = await fetch('/api/v1/firms/account-types')
      const data = await response.json()
      setAccountTypes(data.account_types)
    } catch (err) {
      console.error('Failed to load account types:', err)
    }
  }

  const loadFirmRules = async (firmId: string, accountType: string) => {
    try {
      const response = await fetch(`/api/v1/firms/${firmId}/rules?account_type=${accountType}`)
      const data = await response.json()
      setSelectedFirmRules(data.rules)
    } catch (err) {
      console.error('Failed to load firm rules:', err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await createAccount(token!, {
        platform,
        accountId,
        accountName,
        firm: selectedFirm,
        accountType: selectedAccountType,
        accountSize,
        ruleSetVersion: '1.0',
        username: '', // Not needed for NinjaTrader
        password: '', // Not needed for NinjaTrader
      })

      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect account')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const selectedFirmInfo = firms.find((f) => f.id === selectedFirm)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Connect Account</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Platform
            </label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            >
              <option value="ninjatrader">NinjaTrader</option>
              <option value="tradovate" disabled>Tradovate (Coming Soon)</option>
              <option value="rithmic" disabled>Rithmic (Coming Soon)</option>
            </select>
          </div>

          {/* Prop Firm Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prop Firm *
            </label>
            <select
              value={selectedFirm}
              onChange={(e) => setSelectedFirm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            >
              {firms.map((firm) => (
                <option key={firm.id} value={firm.id}>
                  {firm.display_name}
                </option>
              ))}
            </select>
            {selectedFirmInfo && (
              <p className="text-sm text-gray-600 mt-1">{selectedFirmInfo.description}</p>
            )}
          </div>

          {/* Account Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account Type *
            </label>
            <select
              value={selectedAccountType}
              onChange={(e) => setSelectedAccountType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            >
              {accountTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.display_name} - {type.description}
                </option>
              ))}
            </select>
          </div>

          {/* Firm Rules Preview */}
          {selectedFirmRules && (
            <div className="bg-blue-50 border border-blue-200 rounded p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                Rules for {selectedFirmInfo?.display_name} ({selectedAccountType})
              </h3>
              <div className="space-y-2 text-sm">
                {selectedFirmRules.trailing_drawdown && (
                  <div>
                    <span className="font-medium">Trailing Drawdown:</span>{' '}
                    {selectedFirmRules.trailing_drawdown.max_drawdown_percent}%
                    {selectedFirmRules.trailing_drawdown.include_unrealized_pnl
                      ? ' (includes unrealized PnL)'
                      : ' (end-of-day)'}
                  </div>
                )}
                {selectedFirmRules.daily_loss_limit && (
                  <div>
                    <span className="font-medium">Daily Loss Limit:</span> $
                    {selectedFirmRules.daily_loss_limit.max_loss_amount.toLocaleString()}
                    {' '}(resets at {selectedFirmRules.daily_loss_limit.reset_time})
                  </div>
                )}
                {selectedFirmInfo?.rules_summary.consistency && (
                  <div>
                    <span className="font-medium">Consistency Rule:</span>{' '}
                    {selectedFirmInfo.rules_summary.consistency}
                  </div>
                )}
                {selectedFirmInfo?.rules_summary.news_trading && (
                  <div>
                    <span className="font-medium">News Trading:</span>{' '}
                    {selectedFirmInfo.rules_summary.news_trading}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Account Details */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account ID / Name *
            </label>
            <input
              type="text"
              value={accountId}
              onChange={(e) => {
                setAccountId(e.target.value)
                if (!accountName) setAccountName(e.target.value)
              }}
              placeholder="Your NinjaTrader account name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Display Name
            </label>
            <input
              type="text"
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              placeholder="My Apex Account"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account Size (USD) *
            </label>
            <input
              type="number"
              value={accountSize}
              onChange={(e) => setAccountSize(parseFloat(e.target.value))}
              placeholder="50000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
              min="1000"
              step="1000"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Connecting...' : 'Connect Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

