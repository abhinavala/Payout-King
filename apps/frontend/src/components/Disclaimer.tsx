/**
 * Disclaimer Component
 * 
 * Per Master Plan 7.1: Explicit Disclaimers
 * Always show:
 * - "Advisory, not guaranteed"
 * - "Objective rules only"
 * - "Subjective rules flagged only"
 */

interface DisclaimerProps {
  variant?: 'full' | 'compact' | 'inline'
}

export default function Disclaimer({ variant = 'full' }: DisclaimerProps) {
  if (variant === 'inline') {
    return (
      <span className="text-xs text-gray-500">
        Advisory only. Objective rules only. Not guaranteed.
      </span>
    )
  }

  if (variant === 'compact') {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
        <div className="font-medium mb-1">⚠️ Disclaimer</div>
        <div className="text-xs">
          This platform provides advisory information only. Rules are objective and based on prop firm specifications.
          Subjective rules are flagged but not enforced. No guarantees are provided.
        </div>
      </div>
    )
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
      <div className="font-semibold mb-2 flex items-center gap-2">
        <span>⚠️</span>
        <span>Important Disclaimer</span>
      </div>
      <ul className="list-disc list-inside space-y-1 text-xs">
        <li>
          <strong>Advisory, not guaranteed:</strong> This platform provides advisory information only.
          All rule evaluations and warnings are for informational purposes. We do not guarantee
          accuracy or completeness of rule calculations.
        </li>
        <li>
          <strong>Objective rules only:</strong> This platform evaluates only objective, quantifiable
          rules based on prop firm specifications. We do not enforce or evaluate subjective rules.
        </li>
        <li>
          <strong>Subjective rules flagged only:</strong> If a prop firm has subjective rules (e.g., "no
          overtrading", "good trading behavior"), these may be flagged but are not automatically evaluated.
        </li>
        <li>
          <strong>No liability:</strong> Use of this platform is at your own risk. We are not responsible
          for any trading decisions or account outcomes.
        </li>
      </ul>
    </div>
  )
}
