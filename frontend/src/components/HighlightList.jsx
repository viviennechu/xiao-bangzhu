/**
 * HighlightList — 亮點拖拉排序列表
 * Tasks 9.1, 9.2, 9.3
 */
import { useState } from 'react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

const API = import.meta.env.VITE_API_BASE ?? ''

// ── Sortable card ─────────────────────────────────────────────────────────────

function HighlightCard({ id, title, explanation }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white border border-gray-200 rounded-xl p-4 flex gap-3 shadow-sm"
    >
      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        className="text-gray-300 hover:text-gray-500 cursor-grab active:cursor-grabbing mt-0.5 shrink-0"
        aria-label="拖拉排序"
      >
        ⠿
      </button>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-800 text-sm">{title}</p>
        <p className="text-xs text-gray-500 mt-1">{explanation}</p>
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function HighlightList({ product, highlights, setHighlights }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  async function fetchHighlights() {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/api/highlights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product),
      })
      const data = await res.json()
      setHighlights(
        data.highlights.map((h, i) => ({ ...h, id: `h-${i}` }))
      )
    } catch {
      setError('無法取得亮點，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  function handleDragEnd(event) {
    const { active, over } = event
    if (active.id !== over?.id) {
      setHighlights((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id)
        const newIndex = items.findIndex((i) => i.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  return (
    <div className="bg-gray-50 rounded-2xl shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">② 商品亮點（可拖拉排序）</h2>
        <button
          onClick={fetchHighlights}
          disabled={loading || !product}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '分析中...' : highlights.length ? '重新分析' : 'AI 提取亮點'}
        </button>
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      {highlights.length > 0 ? (
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={highlights.map((h) => h.id)} strategy={verticalListSortingStrategy}>
            <div className="flex flex-col gap-2">
              {highlights.map((h) => (
                <HighlightCard key={h.id} id={h.id} title={h.title} explanation={h.explanation} />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      ) : (
        <p className="text-sm text-gray-400 text-center py-8">
          {product ? '點擊「AI 提取亮點」開始分析' : '請先輸入商品網址'}
        </p>
      )}
    </div>
  )
}
