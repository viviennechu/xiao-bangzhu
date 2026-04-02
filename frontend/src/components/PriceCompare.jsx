/**
 * PriceCompare — 價格比對
 * Tasks 12.1, 12.2, 12.3
 */
import { useState } from 'react'

const API = ''

export default function PriceCompare({ retailPrice, onResult }) {
  const [mode, setMode] = useState('manual') // 'manual' | 'url'
  const [groupBuyPrice, setGroupBuyPrice] = useState('')
  const [groupBuyUrl, setGroupBuyUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleCompare() {
    const retail = parseFloat(retailPrice)
    if (!retail) {
      setError('市售價無效，請確認商品頁有顯示價格')
      return
    }

    setLoading(true)
    setError('')

    try {
      const body = { retail_price: retail }
      if (mode === 'manual') {
        body.group_buy_price = parseFloat(groupBuyPrice)
      } else {
        body.group_buy_url = groupBuyUrl
      }

      const res = await fetch(`${API}/api/price-compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || '比對失敗')
      }

      const data = await res.json()
      setResult(data)
      onResult?.(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">⑤ 價格比對</h2>

      {/* Market price display */}
      <p className="text-sm text-gray-500 mb-4">
        市售價：<span className="font-medium text-gray-800">NT$ {retailPrice || '未取得'}</span>
      </p>

      {/* Mode toggle */}
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setMode('manual')}
          className={`text-xs px-3 py-1 rounded-full border transition-colors ${
            mode === 'manual'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'text-gray-600 border-gray-300 hover:border-blue-400'
          }`}
        >
          手動輸入
        </button>
        <button
          onClick={() => setMode('url')}
          className={`text-xs px-3 py-1 rounded-full border transition-colors ${
            mode === 'url'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'text-gray-600 border-gray-300 hover:border-blue-400'
          }`}
        >
          團購表單網址
        </button>
      </div>

      {/* Input */}
      <div className="flex gap-2">
        {mode === 'manual' ? (
          <input
            type="number"
            value={groupBuyPrice}
            onChange={(e) => setGroupBuyPrice(e.target.value)}
            placeholder="輸入團購價格"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        ) : (
          <input
            type="url"
            value={groupBuyUrl}
            onChange={(e) => setGroupBuyUrl(e.target.value)}
            placeholder="https://... (團購表單網址)"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        )}
        <button
          onClick={handleCompare}
          disabled={loading || (mode === 'manual' ? !groupBuyPrice : !groupBuyUrl)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '比對中...' : '比對'}
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}

      {/* Result */}
      {result && (
        <div className="mt-4">
          {result.is_warning ? (
            <div className="bg-red-50 border border-red-300 rounded-xl px-4 py-3 flex items-start gap-2">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="text-sm font-semibold text-red-700">
                  團購價高於市售價，請洽廠商降價！
                </p>
                <p className="text-xs text-red-500 mt-0.5">
                  團購 NT$ {result.group_buy_price}　市售 NT$ {result.retail_price}
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-300 rounded-xl px-4 py-3">
              <p className="text-sm font-semibold text-green-700">
                比市售價便宜 NT$ {result.savings_amount}（省 {result.savings_percent}%）
              </p>
              <p className="text-xs text-green-500 mt-0.5">
                團購 NT$ {result.group_buy_price}　市售 NT$ {result.retail_price}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
