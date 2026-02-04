import { useState, useEffect } from 'react'

function ProductList({ refreshKey, onSelectProduct }) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [postingId, setPostingId] = useState(null)

  useEffect(() => {
    fetchProducts()
  }, [refreshKey])

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
        // Update product status in list
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
    if (!confirm('Are you sure you want to delete this product? This cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setProducts(products.filter(p => p.id !== productId))
      } else {
        alert('Failed to delete product')
      }
    } catch (err) {
      console.error('Failed to delete product:', err)
      alert('Failed to delete product')
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

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        Loading products...
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        No products yet. Paste a URL above to get started!
      </div>
    )
  }

  // Group products by status
  const readyToPost = products.filter(p => p.status === 'ready_to_post')
  const posted = products.filter(p => p.status === 'posted')
  const inProgress = products.filter(p => ['pending', 'collected'].includes(p.status))
  const failed = products.filter(p => p.status === 'failed')

  const renderProductTable = (productList) => (
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
        {productList.map((product) => (
          <tr key={product.id} className="hover:bg-gray-50">
            <td className="px-6 py-4">
              <div className="flex items-center gap-3">
                {/* Thumbnail */}
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
                {/* Product Info */}
                <div className="min-w-0 flex-1 max-w-md">
                  <div className="text-sm font-medium text-gray-900 truncate" title={product.title}>
                    {product.title || 'Untitled'}
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
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                Source
              </a>
              {onSelectProduct && (
                <button
                  onClick={() => onSelectProduct(product)}
                  className="text-gray-600 hover:text-gray-900 cursor-pointer"
                >
                  View
                </button>
              )}
              {(product.status === 'ready_to_post' || product.status === 'posted') && (
                <button
                  onClick={() => handlePost(product.id)}
                  disabled={postingId === product.id}
                  className="text-blue-600 hover:text-blue-900 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
  )

  return (
    <div className="space-y-6">
      {/* Ready to Post Section */}
      {readyToPost.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-green-50 border-b border-green-200">
            <h3 className="text-lg font-semibold text-green-900">
              Ready to Post ({readyToPost.length})
            </h3>
          </div>
          {renderProductTable(readyToPost)}
        </div>
      )}

      {/* In Progress Section */}
      {inProgress.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900">
              In Progress ({inProgress.length})
            </h3>
          </div>
          {renderProductTable(inProgress)}
        </div>
      )}

      {/* Posted Section */}
      {posted.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-purple-50 border-b border-purple-200">
            <h3 className="text-lg font-semibold text-purple-900">
              Posted ({posted.length})
            </h3>
          </div>
          {renderProductTable(posted)}
        </div>
      )}

      {/* Failed Section */}
      {failed.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-red-50 border-b border-red-200">
            <h3 className="text-lg font-semibold text-red-900">
              Failed ({failed.length})
            </h3>
          </div>
          {renderProductTable(failed)}
        </div>
      )}
    </div>
  )
}

export default ProductList
