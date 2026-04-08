import { useState } from 'react'
import ProductInput from './components/ProductInput'
import ProductInfo from './components/ProductInfo'
import HighlightList from './components/HighlightList'
import ShootingChecklist from './components/ShootingChecklist'
import SocialReferences from './components/SocialReferences'
import PriceCompare from './components/PriceCompare'
import MarketAnalysis from './components/MarketAnalysis'
import MultiFormatOutput from './components/MultiFormatOutput'
import Translator from './components/Translator'

export default function App() {
  const [product, setProduct] = useState(null)
  const [highlights, setHighlights] = useState([])
  const [priceResult, setPriceResult] = useState(null)
  const [marketData, setMarketData] = useState(null)

  function handleAnalysis({ market, competitor }) {
    setMarketData({ market, competitor })
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">寫文小幫手</h1>
          <p className="text-sm text-gray-500 mt-1">輸入商品，自動產出 Blog 長文、社群短文、Reels 腳本</p>
        </div>

        {/* 大V 翻譯機 */}
        <div className="mb-8">
          <Translator />
        </div>

        <hr className="border-gray-200 mb-8" />

        {/* Step 1: Product URL */}
        <div className="mb-4">
          <ProductInput onProductLoaded={setProduct} />
        </div>

        {/* Product info (shown after scrape) */}
        {product && (
          <div className="mb-4">
            <ProductInfo product={product} />
          </div>
        )}

        {/* Step 2: Highlights */}
        <div className="mb-4">
          <HighlightList
            product={product}
            highlights={highlights}
            setHighlights={setHighlights}
          />
        </div>

        {/* Steps 3 & 4: Shooting + Social (side by side on desktop) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <ShootingChecklist highlights={highlights} />
          <SocialReferences productName={product?.name || ''} />
        </div>

        {/* Step 5: Price compare */}
        <div className="mb-4">
          <PriceCompare
            retailPrice={product?.price || ''}
            productName={product?.name || ''}
            onResult={setPriceResult}
          />
        </div>

        {/* Step 6: Market analysis */}
        <div className="mb-4">
          <MarketAnalysis
            productName={product?.name || ''}
            priceResult={priceResult}
            onAnalysis={handleAnalysis}
          />
        </div>

        {/* Step 7: Three-format output */}
        <div className="mb-4">
          <MultiFormatOutput
            product={product}
            highlights={highlights}
            priceResult={priceResult}
            marketAnalysis={marketData?.market || null}
            competitorComparison={marketData?.competitor?.comparison || null}
          />
        </div>
      </div>
    </div>
  )
}
