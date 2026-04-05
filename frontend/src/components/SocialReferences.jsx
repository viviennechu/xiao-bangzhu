/**
 * SocialReferences — 社群素材參考
 * Tasks 11.1, 11.2
 */
import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

function ReferenceCard({ title, url }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="block border border-gray-200 rounded-xl p-3 hover:bg-blue-50 hover:border-blue-300 transition-colors"
    >
      <p className="text-sm font-medium text-blue-700 line-clamp-2">{title}</p>
      <p className="text-xs text-gray-400 mt-1 truncate">{url}</p>
    </a>
  )
}

export default function SocialReferences({ productName }) {
  const [refs, setRefs] = useState(null)
  const [unavailable, setUnavailable] = useState(false)
  const [loading, setLoading] = useState(false)

  async function fetchRefs() {
    if (!productName) return
    setLoading(true)
    setUnavailable(false)
    try {
      const res = await fetch(`${API}/api/social-references`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName }),
      })
      const data = await res.json()
      if (data.error) {
        setUnavailable(true)
        setRefs([])
      } else {
        setRefs(data.references || [])
      }
    } catch {
      setUnavailable(true)
      setRefs([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">④ 社群素材參考</h2>
        <button
          onClick={fetchRefs}
          disabled={loading || !productName}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '搜尋中...' : refs !== null ? '重新搜尋' : '搜尋素材'}
        </button>
      </div>

      {unavailable && (
        <p className="text-sm text-orange-500">素材搜尋暫時無法使用</p>
      )}

      {refs !== null && !unavailable && (
        refs.length > 0 ? (
          <div className="flex flex-col gap-2">
            {refs.map((ref, i) => (
              <ReferenceCard key={i} title={ref.title} url={ref.url} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">找不到相關素材</p>
        )
      )}

      {refs === null && (
        <p className="text-sm text-gray-400 text-center py-8">
          {productName ? '點擊「搜尋素材」找小紅書 / IG 參考' : '請先輸入商品網址'}
        </p>
      )}
    </div>
  )
}
