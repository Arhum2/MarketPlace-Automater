import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ProductCard from '../components/ProductCard'

function ProductsPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [postingId, setPostingId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/products')
      if (response.ok) {
        const data = await response.json()
        setProducts(data)
      }
    } catch (err) {
      console.error('Failed to fetch products:', err)
    } finally {
      setLoading(false)
    }
  }

  const handlePost = async (productId) => {
    if (!confirm('Post this product to Facebook Marketplace?')) return

    setPostingId(productId)

    try {
      const response = await fetch(`/api/products/${productId}/post`, {
        method: 'POST'
      })

      if (response.ok) {
        setProducts(products.map(p =>
          p.id === productId ? { ...p, status: 'posted' } : p
        ))
        alert('Product posted successfully!')
      } else {
        const error = await response.json()
        alert(`Failed to post: ${error.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to post product:', err)
      alert('Failed to post product')
    } finally {
      setPostingId(null)
    }
  }

  const handleDelete = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setProducts(products.filter(p => p.id !== productId))
        if (selectedProduct?.id === productId) {
          setSelectedProduct(null)
        }
      } else {
        alert('Failed to delete product')
      }
    } catch (err) {
      console.error('Failed to delete product:', err)
      alert('Failed to delete product')
    }
  }

  const handleSelectProduct = async (product) => {
    try {
      const response = await fetch(`/api/products/${product.id}/images`)
      if (response.ok) {
        const images = await response.json()
        setSelectedProduct({ ...product, images })
      } else {
        setSelectedProduct({ ...product, images: [] })
      }
    } catch (err) {
      setSelectedProduct({ ...product, images: [] })
    }
  }

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    collected: 'bg-blue-100 text-blue-800',
    ready_to_post: 'bg-green-100 text-green-800',
    posted: 'bg-purple-100 text-purple-800',
    sold: 'bg-gray-100 text-gray-800',
    failed: 'bg-red-100 text-red-800'
  }

  // Filter products
  const filteredProducts = products.filter(p => {
    if (filter === 'all') return true
    if (filter === 'ready') return p.status === 'ready_to_post'
    if (filter === 'posted') return p.status === 'posted'
    if (filter === 'sold') return p.status === 'sold'
    if (filter === 'pending') return ['pending', 'collected'].includes(p.status)
    return true
  })

  // Count by status
  const counts = {
    all: products.length,
    ready: products.filter(p => p.status === 'ready_to_post').length,
    posted: products.filter(p => p.status === 'posted').length,
    sold: products.filter(p => p.status === 'sold').length,
    pending: products.filter(p => ['pending', 'collected'].includes(p.status)).length
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-900 cursor-pointer"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">All Products</h1>
              <p className="text-gray-500 text-sm">{products.length} total products</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
          >
            + Scrape New
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="max-w-7xl mx-auto px-4 pb-4">
          <div className="flex gap-2">
            {[
              { key: 'all', label: 'All' },
              { key: 'ready', label: 'Ready to Post' },
              { key: 'posted', label: 'Posted' },
              { key: 'sold', label: 'Sold' },
              { key: 'pending', label: 'In Progress' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                  filter === tab.key
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tab.label}
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                  filter === tab.key ? 'bg-white/20' : 'bg-gray-200'
                }`}>
                  {counts[tab.key]}
                </span>
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading products...</div>
        ) : filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p className="text-gray-500">No products found</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
            >
              Scrape Your First Product
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {/* Selected Product Detail View */}
            {selectedProduct && (
              <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold">Product Details</h2>
                  <button
                    onClick={() => setSelectedProduct(null)}
                    className="text-gray-500 hover:text-gray-700 cursor-pointer"
                  >
                    Close
                  </button>
                </div>
                <ProductCard
                  product={selectedProduct}
                  onDelete={handleDelete}
                />
              </div>
            )}

            {/* Product List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredProducts.map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex-shrink-0 w-12 h-12 bg-gray-100 rounded overflow-hidden">
                            {product.thumbnail ? (
                              <img
                                src={product.thumbnail}
                                alt={product.title || 'Product'}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-gray-400">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                              </div>
                            )}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-medium text-gray-900 truncate max-w-xs" title={product.title}>
                              {product.title || 'Untitled'}
                            </div>
                            <div className="text-xs text-gray-500 truncate">
                              {product.url ? new URL(product.url).hostname : '-'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-green-600">
                          {product.price || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[product.status] || 'bg-gray-100'}`}>
                          {product.status?.replaceAll('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(product.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                        <button
                          onClick={() => handleSelectProduct(product)}
                          className="text-gray-600 hover:text-gray-900 cursor-pointer"
                        >
                          View
                        </button>
                        {(product.status === 'ready_to_post' || product.status === 'posted') && (
                          <button
                            onClick={() => handlePost(product.id)}
                            disabled={postingId === product.id}
                            className="text-blue-600 hover:text-blue-900 cursor-pointer disabled:opacity-50"
                          >
                            {postingId === product.id ? 'Posting...' : 'Post'}
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="text-red-600 hover:text-red-900 cursor-pointer"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default ProductsPage