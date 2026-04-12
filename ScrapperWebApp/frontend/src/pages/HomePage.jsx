import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ScrapeForm from '../components/ScrapeForm'
import ProductCard from '../components/ProductCard'

function HomePage() {
  const [currentProduct, setCurrentProduct] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleScrapeComplete = (product) => {
    setCurrentProduct(product)
  }

  const handleDeleteProduct = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setCurrentProduct(null)
      }
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Furniture Scraper
            </h1>
            <p className="text-gray-500 text-sm">
              Scrape and post to Facebook Marketplace
            </p>
          </div>
          <button
            onClick={() => navigate('/products')}
            className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
          >
            View All Products
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4">
        {/* Hero Section with Centered Scrape Form */}
        {!currentProduct && (
          <div className="min-h-[70vh] flex flex-col items-center justify-center py-16">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Start Scraping
              </h2>
              <p className="text-lg text-gray-600 max-w-md mx-auto">
                Paste a product URL from Amazon, Wayfair, or other furniture sites to get started
              </p>
            </div>

            <div className="w-full max-w-2xl">
              <ScrapeForm
                onScrapeComplete={handleScrapeComplete}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                setError={setError}
              />
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg max-w-2xl w-full">
                {error}
                <button
                  onClick={() => setError(null)}
                  className="ml-4 text-red-900 hover:underline cursor-pointer"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Quick Stats */}
            <div className="mt-16 grid grid-cols-3 gap-8 text-center">
              <div className="p-4">
                <div className="text-3xl font-bold text-blue-600">1</div>
                <div className="text-sm text-gray-500 mt-1">Paste URL</div>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold text-purple-600">2</div>
                <div className="text-sm text-gray-500 mt-1">Review & Edit</div>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold text-green-600">3</div>
                <div className="text-sm text-gray-500 mt-1">Post to Facebook</div>
              </div>
            </div>
          </div>
        )}

        {/* Show Product Card after scraping */}
        {currentProduct && (
          <div className="py-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Scraped Product</h2>
              <div className="flex gap-3">
                <button
                  onClick={() => setCurrentProduct(null)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-900 cursor-pointer"
                >
                  Scrape Another
                </button>
                <button
                  onClick={() => navigate('/products')}
                  className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 cursor-pointer"
                >
                  View All Products
                </button>
              </div>
            </div>
            <ProductCard
              product={currentProduct}
              onDelete={handleDeleteProduct}
            />
          </div>
        )}
      </main>
    </div>
  )
}

export default HomePage
