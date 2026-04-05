/**
 * Copywriter — 文案產出、複製、重新生成
 * Tasks 13.1, 13.2, 13.3, 13.4
 */
import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

export default function Copywriter({ product, highlights, priceResult }) {
  const [copy, setCopy] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState('')

  async function generate() {
    if (!highlights.length) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/api/copywrite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product,
          highlights,
          price_result: priceResult || null,
        }),
      })
      const data = await res.json()
      setCopy(data.copy || '')
    } catch {
      setError('文案生成失敗，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(copy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback
      const el = document.createElement('textarea')
      el.value = copy
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">⑥ 產出文案</h2>
        <button
          onClick={generate}
          disabled={loading || !highlights.length}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              生成中...
            </span>
          ) : copy ? '重新生成' : '產出文案'}
        </button>
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      {copy ? (
        <>
          {/* Copy text area */}
          <textarea
            value={copy}
            onChange={(e) => setCopy(e.target.value)}
            rows={16}
            className="w-full font-mono text-sm text-gray-800 border border-gray-200 rounded-xl p-4 resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          {/* Actions */}
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleCopy}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                copied
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {copied ? '已複製 ✓' : '複製文案'}
            </button>
            <button
              onClick={generate}
              disabled={loading}
              className="flex-1 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50"
            >
              重新生成
            </button>
          </div>
        </>
      ) : (
        <p className="text-sm text-gray-400 text-center py-8">
          {highlights.length
            ? '點擊「產出文案」生成 LINE 文章'
            : '請先提取商品亮點'}
        </p>
      )}
    </div>
  )
}
