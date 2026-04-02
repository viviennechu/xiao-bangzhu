/**
 * ProductInfo — 顯示抓取到的商品基本資料
 * Task 8.3
 */
export default function ProductInfo({ product }) {
  if (!product) return null

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">商品資料</h2>
      <div className="flex gap-4">
        {product.images?.[0] && (
          <img
            src={product.images[0]}
            alt={product.name}
            className="w-24 h-24 object-cover rounded-lg border border-gray-200 shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">{product.name || '（無商品名稱）'}</p>
          {product.price && (
            <p className="text-sm text-gray-500 mt-1">市售價：NT$ {product.price}</p>
          )}
          {product.description && (
            <p className="text-xs text-gray-400 mt-2 line-clamp-3">{product.description}</p>
          )}
        </div>
      </div>
    </div>
  )
}
