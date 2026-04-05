import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

const TREND_LABEL = {
  rising: { text: '上升趨勢', color: 'text-green-600', bg: 'bg-green-50' },
  stable: { text: '平穩', color: 'text-yellow-600', bg: 'bg-yellow-50' },
  declining: { text: '下降趨勢', color: 'text-red-500', bg: 'bg-red-50' },
}

const COMPETITION_LABEL = {
  high: { text: '競爭激烈', color: 'text-red-500' },
  medium: { text: '中等競爭', color: 'text-yellow-600' },
  low: { text: '藍海', color: 'text-green-600' },
}

const FORMAT_LABEL = {
  blog: 'Blog 長文',
  social: '社群短文',
  reels: 'Reels 腳本',
}

export default function MarketAnalysis({ productName, priceResult, onAnalysis }) {
  const [analysis, setAnalysis] = useState(null)
  const [competitor, setCompetitor] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function runAnalysis() {
    if (!productName) return
    setLoading(true)
    setError('')

    try {
      const [marketRes, competitorRes] = await Promise.all([
        fetch(`${API}/api/market-analysis?keyword=${encodeURIComponent(productName)}`),
        fetch(`${API}/api/competitor-price?keyword=${encodeURIComponent(productName)}${
          priceResult?.group_buy_price ? `&group_buy_price=${priceResult.group_buy_price}` : ''
        }`),
      ])

      const marketData = await marketRes.json()
      const competitorData = await competitorRes.json()

      setAnalysis(marketData)
      setCompetitor(competitorData)

      if (onAnalysis) {
        onAnalysis({ market: marketData, competitor: competitorData })
      }
    } catch {
      setError('分析失敗，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  const trend = analysis?.trend_direction ? TREND_LABEL[analysis.trend_direction] : null
  const competition = analysis?.social_competition ? COMPETITION_LABEL[analysis.social_competition] : null

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">市場分析</h2>
        <button
          onClick={runAnalysis}
          disabled={loading || !productName}
          className="bg-purple-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              分析中...
            </span>
          ) : analysis ? '重新分析' : '開始分析'}
        </button>
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      {!analysis && !loading && (
        <p className="text-sm text-gray-400 text-center py-6">
          {productName ? '點擊「開始分析」取得市場趨勢與行銷建議' : '請先輸入商品名稱'}
        </p>
      )}

      {analysis && (
        <div className="space-y-4">
          {/* Trend + Social signals */}
          <div className="grid grid-cols-2 gap-3">
            <div className={`rounded-xl p-3 ${trend?.bg || 'bg-gray-50'}`}>
              <p className="text-xs text-gray-500 mb-1">Google 趨勢</p>
              <p className={`font-semibold ${trend?.color || 'text-gray-400'}`}>
                {trend?.text || '無資料'}
              </p>
              {analysis.avg_score != null && (
                <p className="text-xs text-gray-400 mt-0.5">熱度 {analysis.avg_score}/100</p>
              )}
            </div>
            <div className="rounded-xl p-3 bg-gray-50">
              <p className="text-xs text-gray-500 mb-1">IG 競爭度</p>
              <p className={`font-semibold ${competition?.color || 'text-gray-400'}`}>
                {competition?.text || '無資料'}
              </p>
            </div>
          </div>

          {/* Recommended formats */}
          {analysis.recommended_formats?.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">建議推廣格式</p>
              <div className="flex flex-wrap gap-2">
                {analysis.recommended_formats.map((fmt) => (
                  <span
                    key={fmt}
                    className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium"
                  >
                    {FORMAT_LABEL[fmt] || fmt}
                  </span>
                ))}
              </div>
              {analysis.strategy_type && (
                <p className="text-xs text-gray-500 mt-2">
                  策略：<span className="text-gray-700">{analysis.strategy_type}</span>
                </p>
              )}
            </div>
          )}

          {/* Competitor price */}
          {competitor && (
            <div className="border-t pt-3">
              <p className="text-xs text-gray-500 mb-1">競品比價（chienchien99）</p>
              {competitor.competitor_price ? (
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    對手團購價：NT${competitor.competitor_price.toLocaleString()}
                    {competitor.from_cache && (
                      <span className="ml-1 text-xs text-gray-400">（快取）</span>
                    )}
                  </p>
                  {competitor.comparison && (
                    <p className={`text-xs mt-1 ${
                      competitor.comparison.is_competitive ? 'text-green-600' : 'text-orange-500'
                    }`}>
                      {competitor.comparison.recommendation}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-xs text-gray-400">查無歷史團購紀錄</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
