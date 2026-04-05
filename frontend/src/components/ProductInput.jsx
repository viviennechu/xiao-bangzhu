/**
 * ProductInput — 支援「商品網址」或「品名關鍵字」兩種輸入模式
 */
import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

function isUrl(str) {
  return str.startsWith('http://') || str.startsWith('https://')
}

export default function ProductInput({ onProductLoaded }) {
  const [input, setInput] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const val = input.trim()
    if (!val) return

    setLoading(true)
    setError('')
    setStatus('正在取得商品資料...')

    if (isUrl(val)) {
      await scrapeUrl(val)
    } else {
      await searchByName(val)
    }
  }

  async function scrapeUrl(url) {
    try {
      const es = new EventSource(`${API}/api/scrape?url=${encodeURIComponent(url)}`)
      let appErrorHandled = false

      es.addEventListener('progress', (e) => {
        setStatus(JSON.parse(e.data).message)
      })

      es.addEventListener('done', (e) => {
        appErrorHandled = true
        es.close()
        setLoading(false)
        setStatus('完成')
        onProductLoaded(JSON.parse(e.data))
      })

      es.addEventListener('error', (e) => {
        appErrorHandled = true
        es.close()
        setLoading(false)
        setError(e.data ? JSON.parse(e.data).message : '無法取得商品資料，請手動輸入')
        setStatus('')
      })

      es.onerror = () => {
        setTimeout(() => {
          if (appErrorHandled) return
          es.close()
          setLoading(false)
          setError('連線失敗，請確認後端服務是否啟動')
          setStatus('')
        }, 200)
      }
    } catch (err) {
      setLoading(false)
      setError('發生錯誤：' + err.message)
      setStatus('')
    }
  }

  async function searchByName(name) {
    try {
      const res = await fetch(`${API}/api/search-product?name=${encodeURIComponent(name)}`)
      if (!res.ok) throw new Error(await res.text())
      const product = await res.json()
      setLoading(false)
      setStatus('完成')
      onProductLoaded(product)
    } catch (err) {
      setLoading(false)
      setError('搜尋失敗，請直接在下方手動填入商品資訊')
      setStatus('')
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">① 輸入商品網址或品名</h2>
      <p className="text-xs text-gray-400 mb-3">貼上商品連結，或直接打品名讓系統搜尋</p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="https://... 或輸入品名，例如：ANPANMAN 積木樂趣組"
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? '搜尋中...' : '分析'}
        </button>
      </form>

      {status && (
        <p className="mt-2 text-sm text-blue-600 flex items-center gap-1">
          {loading && <span className="inline-block w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
          {status}
        </p>
      )}
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  )
}
