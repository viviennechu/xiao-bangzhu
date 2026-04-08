/**
 * PriceCompare — 多平台比價 + 團購價比對
 */
import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

export default function PriceCompare({ retailPrice, productName, onResult }) {
  const [mode, setMode] = useState('manual')
  const [manualRetail, setManualRetail] = useState('')
  const [groupBuyPrice, setGroupBuyPrice] = useState('')
  const [groupBuyUrl, setGroupBuyUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [platforms, setPlatforms] = useState([])
  const [platformLoading, setPlatformLoading] = useState(false)
  const [localName, setLocalName] = useState('')

  const searchName = productName || localName

  async function handleSearchPlatforms() {
    if (!searchName) return
    setPlatformLoading(true)
    setPlatforms([])
    try {
      const res = await fetch(`${API}/api/platform-prices?name=${encodeURIComponent(searchName)}`)
      const data = await res.json()
      setPlatforms(data.platforms || [])
      // 自動填入最低市售價
      if (data.platforms?.length > 0 && !manualRetail && !retailPrice) {
        setManualRetail(String(data.platforms[0].price))
      }
    } catch {
      // silent
    } finally {
      setPlatformLoading(false)
    }
  }

  async function handleCompare() {
    const retail = parseFloat(retailPrice) || parseFloat(manualRetail)
    if (!retail) {
      setError('請輸入市售價')
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

  const effectiveRetail = parseFloat(retailPrice) || parseFloat(manualRetail)

  return (
    <div className="bg-white rounded-2xl shadow p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">⑤ 價格比對</h2>

      {/* Platform price search */}
      <div>
        <p className="text-xs text-gray-500 mb-1">各平台最低售價（自動比價）</p>
        {!productName && (
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={localName}
              onChange={(e) => setLocalName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchPlatforms()}
              placeholder="輸入商品名稱，例：樂高得寶火車"
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
            <button
              onClick={handleSearchPlatforms}
              disabled={platformLoading || !localName}
              className="text-sm px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {platformLoading ? '查詢中...' : '🔍 查價'}
            </button>
          </div>
        )}
        {productName && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">{productName}</span>
            <button
              onClick={handleSearchPlatforms}
              disabled={platformLoading}
              className="text-xs px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 disabled:opacity-50 transition-colors"
            >
              {platformLoading ? '查詢中...' : '🔍 自動查價'}
            </button>
          </div>
        )}
        {platforms.length > 0 && (
          <div className="rounded-xl border border-gray-100 overflow-hidden mb-2">
            {platforms.map((p, i) => (
              <div key={p.platform} className={`flex items-center justify-between px-3 py-2 text-sm ${i === 0 ? 'bg-amber-50' : 'bg-white'} ${i < platforms.length - 1 ? 'border-b border-gray-100' : ''}`}>
                <span className="text-gray-600 flex items-center gap-1">
                  {i === 0 && <span className="text-amber-500 text-xs">最低</span>}
                  <a href={p.url} target="_blank" rel="noreferrer" className="hover:underline">{p.platform}</a>
                </span>
                <span className="font-medium text-gray-800">NT$ {p.price.toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Retail price */}
      {retailPrice ? (
        <p className="text-sm text-gray-500">
          市售價：<span className="font-medium text-gray-800">NT$ {retailPrice}</span>
        </p>
      ) : (
        <div>
          <label className="text-xs text-gray-500 mb-1 block">市售價（用於比對，可從上方查到的最低價填入）</label>
          <input
            type="number"
            value={manualRetail}
            onChange={(e) => setManualRetail(e.target.value)}
            placeholder="例：1500"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Group buy price input */}
      <div>
        <div className="flex gap-2 mb-2">
          <button onClick={() => setMode('manual')} className={`text-xs px-3 py-1 rounded-full border transition-colors ${mode === 'manual' ? 'bg-blue-600 text-white border-blue-600' : 'text-gray-600 border-gray-300'}`}>手動輸入</button>
          <button onClick={() => setMode('url')} className={`text-xs px-3 py-1 rounded-full border transition-colors ${mode === 'url' ? 'bg-blue-600 text-white border-blue-600' : 'text-gray-600 border-gray-300'}`}>團購表單網址</button>
        </div>
        <div className="flex gap-2">
          {mode === 'manual' ? (
            <input type="number" value={groupBuyPrice} onChange={(e) => setGroupBuyPrice(e.target.value)} placeholder="輸入團購價格" className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          ) : (
            <input type="text" value={groupBuyUrl} onChange={(e) => setGroupBuyUrl(e.target.value)} placeholder="https://... (團購表單網址)" className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          )}
          <button onClick={handleCompare} disabled={loading || !effectiveRetail || (mode === 'manual' ? !groupBuyPrice : !groupBuyUrl)} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? '比對中...' : '比對'}
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {result && (
        <div>
          {result.is_warning ? (
            <div className="bg-red-50 border border-red-300 rounded-xl px-4 py-3 flex items-start gap-2">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="text-sm font-semibold text-red-700">團購價高於市售價，請洽廠商降價！</p>
                <p className="text-xs text-red-500 mt-0.5">團購 NT$ {result.group_buy_price}　市售 NT$ {result.retail_price}</p>
              </div>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-300 rounded-xl px-4 py-3">
              <p className="text-sm font-semibold text-green-700">比市售價便宜 NT$ {result.savings_amount}（省 {result.savings_percent}%）</p>
              <p className="text-xs text-green-500 mt-0.5">團購 NT$ {result.group_buy_price}　市售 NT$ {result.retail_price}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
