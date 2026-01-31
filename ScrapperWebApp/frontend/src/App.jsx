import { useState } from 'react'
import ScrapeForm from './components/ScrapeForm'
import ProductCard from './components/ProductCard'
import ProductList from './components/ProductList'

function App() {
  const [currentProduct, setCurrentProduct] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleScrapeComplete = (product) => {
    setCurrentProduct(product)
    setRefreshKey(prev => prev + 1) // Trigger product list refresh
  }

  const handleSelectProduct = async (product) => {
    // Fetch images for the product
    try {
      const response = await fetch(`/api/products/${product.id}/images`)
      if (response.ok) {
        const images = await response.json()
        setCurrentProduct({ ...product, images })
      } else {
        setCurrentProduct({ ...product, images: [] })
      }
    } catch (err) {
      setCurrentProduct({ ...product, images: [] })
    }
  }

  const handleDeleteProduct = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        if (currentProduct?.id === productId) {
          setCurrentProduct(null)
        }
        setRefreshKey(prev => prev + 1)
      }
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Furniture Scraper
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Scrape product data from Amazon, Wayfair, and more
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Scrape Form */}
        <ScrapeForm
          onScrapeComplete={handleScrapeComplete}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          setError={setError}
        />

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-900 hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Current Product */}
        {currentProduct && (
          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Selected Product</h2>
              <button
                onClick={() => setCurrentProduct(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>
            <ProductCard
              product={currentProduct}
              onDelete={handleDeleteProduct}
            />
          </div>
        )}

        {/* All Products */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">All Products</h2>
          <ProductList
            refreshKey={refreshKey}
            onSelectProduct={handleSelectProduct}
          />
        </div>
      </main>
    </div>
  )
}

export default App
