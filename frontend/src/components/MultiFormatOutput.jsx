import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

const TABS = [
  { key: 'blog', label: 'Blog 長文' },
  { key: 'social', label: '社群短文' },
  { key: 'reels', label: 'Reels 腳本' },
]

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text)
    } catch {
      const el = document.createElement('textarea')
      el.value = text
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
        copied ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      {copied ? '已複製 ✓' : '複製'}
    </button>
  )
}

function BlogOutput({ data }) {
  if (!data) return <p className="text-sm text-gray-400 text-center py-8">尚未生成</p>
  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs text-gray-500">SEO 標題</p>
          <p className="font-semibold text-gray-800">{data.title}</p>
        </div>
        <CopyButton text={data.title} />
      </div>
      {data.meta_description && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Meta Description</p>
          <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-2">{data.meta_description}</p>
        </div>
      )}
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">文章內容</p>
        <CopyButton text={data.content} />
      </div>
      <textarea
        value={data.content}
        readOnly
        rows={18}
        className="w-full font-mono text-sm text-gray-800 border border-gray-200 rounded-xl p-3 resize-y focus:outline-none"
      />
    </div>
  )
}

function SocialOutput({ data }) {
  if (!data) return <p className="text-sm text-gray-400 text-center py-8">尚未生成</p>

  const platforms = [
    { key: 'ig_post', label: 'Instagram' },
    { key: 'fb_post', label: 'Facebook' },
    { key: 'line_post', label: 'LINE 群組' },
  ]

  return (
    <div className="space-y-4">
      {platforms.map(({ key, label }) => (
        <div key={key}>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-medium text-gray-500">{label}</p>
            <CopyButton text={data[key] || ''} />
          </div>
          <textarea
            value={data[key] || ''}
            readOnly
            rows={5}
            className="w-full text-sm text-gray-800 border border-gray-200 rounded-xl p-3 resize-y focus:outline-none"
          />
        </div>
      ))}
    </div>
  )
}

function ReelsOutput({ data }) {
  if (!data) return <p className="text-sm text-gray-400 text-center py-8">尚未生成</p>

  const fullScript = [
    `【Hook】\n${data.hook || ''}`,
    ...(data.segments || []).map((seg, i) =>
      `【第 ${i + 1} 段】\n旁白：${seg.voiceover || ''}\n畫面：${seg.screen_hint || ''}`
    ),
    `【CTA】\n${data.cta || ''}`,
  ].join('\n\n')

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">完整腳本</p>
        <CopyButton text={fullScript} />
      </div>

      {/* Hook */}
      <div className="bg-yellow-50 rounded-xl p-3">
        <p className="text-xs font-medium text-yellow-700 mb-1">Hook（3 秒開場）</p>
        <p className="text-sm text-gray-800">{data.hook}</p>
      </div>

      {/* Segments */}
      {(data.segments || []).map((seg, i) => (
        <div key={i} className="border border-gray-100 rounded-xl p-3">
          <p className="text-xs font-medium text-gray-500 mb-2">第 {i + 1} 段</p>
          <p className="text-sm text-gray-800 mb-1">{seg.voiceover}</p>
          <p className="text-xs text-gray-400">📹 {seg.screen_hint}</p>
        </div>
      ))}

      {/* CTA */}
      <div className="bg-blue-50 rounded-xl p-3">
        <p className="text-xs font-medium text-blue-700 mb-1">CTA</p>
        <p className="text-sm text-gray-800">{data.cta}</p>
      </div>
    </div>
  )
}

export default function MultiFormatOutput({ product, highlights, priceResult, marketAnalysis, competitorComparison }) {
  const [activeTab, setActiveTab] = useState('blog')
  const [outputs, setOutputs] = useState({ blog: null, social: null, reels: null })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  async function generateAll() {
    if (!highlights.length) return
    setLoading(true)
    setErrors({})

    try {
      const res = await fetch(`${API}/api/generate/all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product,
          highlights,
          price_result: priceResult || null,
          market_analysis: marketAnalysis || null,
          competitor_comparison: competitorComparison || null,
        }),
      })
      const data = await res.json()
      setOutputs({
        blog: data.blog || null,
        social: data.social || null,
        reels: data.reels || null,
      })
      if (data.errors && Object.keys(data.errors).length > 0) {
        setErrors(data.errors)
      }
    } catch {
      setErrors({ general: '生成失敗，請稍後再試' })
    } finally {
      setLoading(false)
    }
  }

  const hasOutput = Object.values(outputs).some(Boolean)

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">產出內容</h2>
        <button
          onClick={generateAll}
          disabled={loading || !highlights.length}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              生成中（三格式並行）...
            </span>
          ) : hasOutput ? '重新生成全部' : '一鍵產出三格式'}
        </button>
      </div>

      {errors.general && <p className="text-sm text-red-500 mb-3">{errors.general}</p>}

      {!hasOutput && !loading && (
        <p className="text-sm text-gray-400 text-center py-8">
          {highlights.length ? '點擊「一鍵產出三格式」同時生成 Blog、社群文、Reels 腳本' : '請先提取商品亮點'}
        </p>
      )}

      {hasOutput && (
        <>
          {/* Tabs */}
          <div className="flex gap-1 mb-4 bg-gray-100 rounded-xl p-1">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
                {errors[tab.key] && <span className="ml-1 text-red-400">!</span>}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {errors[activeTab] && (
            <p className="text-sm text-red-500 mb-3">{errors[activeTab]}</p>
          )}
          {activeTab === 'blog' && <BlogOutput data={outputs.blog} />}
          {activeTab === 'social' && <SocialOutput data={outputs.social} />}
          {activeTab === 'reels' && <ReelsOutput data={outputs.reels} />}
        </>
      )}
    </div>
  )
}
