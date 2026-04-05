/**
 * ShootingChecklist — 拍攝清單（照片 + 影片）
 * Tasks 10.1, 10.2, 10.3
 */
import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE ?? ''

function CheckItem({ item, checked, onToggle }) {
  return (
    <label className="flex items-start gap-2 cursor-pointer group">
      <input
        type="checkbox"
        checked={checked}
        onChange={onToggle}
        className="mt-0.5 accent-blue-600"
      />
      <span className={`text-sm ${checked ? 'line-through text-gray-400' : 'text-gray-700'}`}>
        {item.shot}
        {item.highlight && (
          <span className="ml-1 text-xs text-gray-400">({item.highlight})</span>
        )}
      </span>
    </label>
  )
}

export default function ShootingChecklist({ highlights }) {
  const [plan, setPlan] = useState(null)
  const [checked, setChecked] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function fetchPlan() {
    if (!highlights.length) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/api/shooting-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ highlights }),
      })
      const data = await res.json()
      setPlan(data)
      setChecked({})
    } catch {
      setError('無法產生拍攝清單，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  function toggle(key) {
    setChecked((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const allItems = plan
    ? [
        ...(plan.photos || []).map((item, i) => ({ ...item, key: `photo-${i}` })),
        ...(plan.videos || []).map((item, i) => ({ ...item, key: `video-${i}` })),
      ]
    : []

  const allChecked = allItems.length > 0 && allItems.every((item) => checked[item.key])

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">③ 拍攝清單</h2>
        <button
          onClick={fetchPlan}
          disabled={loading || !highlights.length}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '生成中...' : plan ? '重新生成' : '產生清單'}
        </button>
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      {allChecked && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg px-4 py-2 text-sm text-green-700 font-medium">
          拍攝完成 ✓
        </div>
      )}

      {plan ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Photos */}
          <div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-1">
              📷 照片
            </h3>
            <div className="flex flex-col gap-2">
              {(plan.photos || []).map((item, i) => (
                <CheckItem
                  key={`photo-${i}`}
                  item={item}
                  checked={!!checked[`photo-${i}`]}
                  onToggle={() => toggle(`photo-${i}`)}
                />
              ))}
            </div>
          </div>

          {/* Videos */}
          <div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-1">
              🎬 影片
            </h3>
            <div className="flex flex-col gap-2">
              {(plan.videos || []).map((item, i) => (
                <CheckItem
                  key={`video-${i}`}
                  item={item}
                  checked={!!checked[`video-${i}`]}
                  onToggle={() => toggle(`video-${i}`)}
                />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-400 text-center py-8">
          {highlights.length ? '點擊「產生清單」建立拍攝計畫' : '請先提取商品亮點'}
        </p>
      )}
    </div>
  )
}
