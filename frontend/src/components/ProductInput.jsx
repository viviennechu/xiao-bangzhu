/**
 * ProductInput — URL 輸入表單 + SSE 進度條
 * Tasks 8.1, 8.2, 8.3
 */
import { useState } from 'react'

const API = ''

export default function ProductInput({ onProductLoaded }) {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('') // progress message
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError('')
    setStatus('正在抓取商品資料...')

    try {
      const es = new EventSource(`${API}/api/scrape?url=${encodeURIComponent(url)}`)
      let appErrorHandled = false

      es.addEventListener('progress', (e) => {
        const data = JSON.parse(e.data)
        setStatus(data.message)
      })

      es.addEventListener('done', (e) => {
        appErrorHandled = true
        const product = JSON.parse(e.data)
        es.close()
        setLoading(false)
        setStatus('完成')
        onProductLoaded(product)
      })

      es.addEventListener('error', (e) => {
        appErrorHandled = true
        es.close()
        setLoading(false)
        if (e.data) {
          const data = JSON.parse(e.data)
          setError(data.message || '抓取失敗')
        } else {
          setError('無法取得商品資料，請手動輸入')
        }
        setStatus('')
      })

      // Native SSE error (network) — delay to let custom error event fire first
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

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">① 輸入商品網址</h2>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.momo.com.tw/goods/..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? '抓取中...' : '分析'}
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
