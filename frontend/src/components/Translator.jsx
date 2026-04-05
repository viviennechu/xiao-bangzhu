import { useState } from 'react'

const FORMATS = [
  { key: 'blog', label: 'FB文／Blog' },
  { key: 'ig_stories', label: 'IG 限動腳本' },
  { key: 'group_fire', label: '群組生火' },
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

function BlogResult({ data }) {
  if (!data) return null
  const text = [data.title, data.content].filter(Boolean).join('\n\n')
  return (
    <div className="space-y-3">
      {data.title && (
        <div className="flex items-start justify-between gap-2">
          <p className="font-semibold text-gray-800">{data.title}</p>
          <CopyButton text={data.title} />
        </div>
      )}
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">文章內容</p>
        <CopyButton text={text} />
      </div>
      <textarea
        value={data.content || ''}
        readOnly
        rows={20}
        className="w-full font-mono text-sm text-gray-800 border border-gray-200 rounded-xl p-3 resize-y focus:outline-none"
      />
    </div>
  )
}

function IgStoriesResult({ data }) {
  if (!data?.slides) return null
  const fullScript = data.slides.map(s =>
    `【張${s.index}｜${s.purpose}】\n${s.text}\n視覺：${s.visual}`
  ).join('\n\n')
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">完整腳本（{data.slides.length} 張）</p>
        <CopyButton text={fullScript} />
      </div>
      {data.slides.map((slide) => (
        <div key={slide.index} className="border border-gray-100 rounded-xl p-3 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-400">張 {slide.index}</span>
            <span className="text-xs text-gray-400">｜</span>
            <span className="text-xs text-indigo-600 font-medium">{slide.purpose}</span>
          </div>
          <p className="text-sm text-gray-800 font-medium">{slide.text}</p>
          <p className="text-xs text-gray-400">📷 {slide.visual}</p>
        </div>
      ))}
    </div>
  )
}

function GroupFireResult({ data }) {
  if (!data?.content) return null
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">群組貼文</p>
        <CopyButton text={data.content} />
      </div>
      <textarea
        value={data.content}
        readOnly
        rows={8}
        className="w-full text-sm text-gray-800 border border-gray-200 rounded-xl p-3 resize-y focus:outline-none"
      />
    </div>
  )
}

export default function Translator() {
  const [draft, setDraft] = useState('')
  const [persona, setPersona] = useState('bigv')
  const [activeFormat, setActiveFormat] = useState('blog')
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleGenerate() {
    if (!draft.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, persona, output_format: activeFormat }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setResults(prev => ({ ...prev, [`${persona}_${activeFormat}`]: data }))
    } catch (e) {
      setError('生成失敗，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  const currentKey = `${persona}_${activeFormat}`
  const currentResult = results[currentKey]

  return (
    <div className="bg-white rounded-2xl shadow p-6 space-y-5">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800">大V 翻譯機</h2>
        <p className="text-xs text-gray-400 mt-0.5">貼上助理草稿，選人設和格式，一鍵改寫</p>
      </div>

      {/* Draft input */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">助理草稿</label>
        <textarea
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder="把助理寫的草稿貼在這裡..."
          rows={8}
          className="w-full text-sm text-gray-800 border border-gray-200 rounded-xl p-3 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>

      {/* Persona selector */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-2 block">口吻</label>
        <div className="flex gap-2">
          <button
            onClick={() => setPersona('bigv')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium border-2 transition-all ${
              persona === 'bigv'
                ? 'border-rose-400 bg-rose-50 text-rose-700'
                : 'border-gray-200 text-gray-500 hover:border-gray-300'
            }`}
          >
            大V
          </button>
          <button
            onClick={() => setPersona('wa')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium border-2 transition-all ${
              persona === 'wa'
                ? 'border-amber-400 bg-amber-50 text-amber-700'
                : 'border-gray-200 text-gray-500 hover:border-gray-300'
            }`}
          >
            WA 宇宸
          </button>
        </div>
      </div>

      {/* Format tabs */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-2 block">格式</label>
        <div className="flex gap-1 bg-gray-100 rounded-xl p-1">
          {FORMATS.map(f => (
            <button
              key={f.key}
              onClick={() => setActiveFormat(f.key)}
              className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                activeFormat === f.key
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={loading || !draft.trim()}
        className="w-full bg-indigo-600 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
            改寫中...
          </span>
        ) : '改寫'}
      </button>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Output */}
      {currentResult && (
        <div className="border-t border-gray-100 pt-5">
          {activeFormat === 'blog' && <BlogResult data={currentResult} />}
          {activeFormat === 'ig_stories' && <IgStoriesResult data={currentResult} />}
          {activeFormat === 'group_fire' && <GroupFireResult data={currentResult} />}
        </div>
      )}
    </div>
  )
}
