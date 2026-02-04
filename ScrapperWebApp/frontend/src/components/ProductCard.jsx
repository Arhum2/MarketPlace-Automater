import { useState } from 'react'

function ProductCard({ product, onUpdate, onDelete }) {
  const [selectedImage, setSelectedImage] = useState(0)
  const [isEditing, setIsEditing] = useState(false)
  const [editedProduct, setEditedProduct] = useState(product)
  const [images, setImages] = useState(product.images || [])
  const [isManagingImages, setIsManagingImages] = useState(false)
  const [isPosting, setIsPosting] = useState(false)
  const [postingStatus, setPostingStatus] = useState('')

  const missingFields = product.missing_fields || []

  const handlePost = async () => {
    if (!confirm('Post this product to Facebook Marketplace?')) return

    setIsPosting(true)
    setPostingStatus('Opening browser and posting...')

    try {
      const response = await fetch(`/api/products/${product.id}/post`, {
        method: 'POST'
      })

      if (response.ok) {
        const result = await response.json()
        setPostingStatus('Posted successfully!')
        // Update local state to reflect posted status
        if (onUpdate) onUpdate({ ...product, status: 'posted' })
      } else {
        const error = await response.json()
        setPostingStatus(`Failed: ${error.detail}`)
      }
    } catch (err) {
      console.error('Posting failed:', err)
      setPostingStatus('Failed to post')
    } finally {
      setIsPosting(false)
      // Clear status after 5 seconds
      setTimeout(() => setPostingStatus(''), 5000)
    }
  }

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/products/${product.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editedProduct.title,
          price: editedProduct.price,
          description: editedProduct.description
        })
      })

      if (response.ok) {
        const updated = await response.json()
        // Update local state with server response
        setEditedProduct(updated)
        if (onUpdate) onUpdate(updated)
      } else {
        alert('Failed to save changes')
      }
    } catch (err) {
      console.error('Save failed:', err)
      alert('Failed to save changes')
    }
    setIsEditing(false)
  }

  const handleDeleteImage = async (imageId, index) => {
    try {
      const response = await fetch(`/api/products/${product.id}/images/${imageId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        const newImages = images.filter((_, i) => i !== index)
        setImages(newImages)
        if (selectedImage >= newImages.length) {
          setSelectedImage(Math.max(0, newImages.length - 1))
        }
      }
    } catch (err) {
      console.error('Failed to delete image:', err)
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

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="md:flex">
        {/* Image Gallery */}
        <div className="md:w-1/3 p-4">
          {images.length > 0 ? (
            <div>
              {/* Main Image */}
              <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-2 relative group">
                <img
                  src={images[selectedImage]?.file_path || images[selectedImage]}
                  alt={product.title || 'Product'}
                  className="w-full h-full object-contain"
                />
                {isManagingImages && (
                  <button
                    onClick={() => handleDeleteImage(images[selectedImage]?.id, selectedImage)}
                    className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                    title="Remove this image"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>

              {/* Thumbnails */}
              {images.length > 1 && (
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {images.map((img, idx) => (
                    <div key={idx} className="relative group">
                      <button
                        onClick={() => setSelectedImage(idx)}
                        className={`flex-shrink-0 w-16 h-16 rounded border-2 overflow-hidden cursor-pointer ${
                          selectedImage === idx ? 'border-blue-500' : 'border-gray-200'
                        }`}
                      >
                        <img
                          src={img?.file_path || img}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      </button>
                      {isManagingImages && (
                        <button
                          onClick={() => handleDeleteImage(img?.id, idx)}
                          className="absolute -top-1 -right-1 bg-red-500 text-white w-5 h-5 rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                          title="Remove"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Image Management Toggle */}
              <button
                onClick={() => setIsManagingImages(!isManagingImages)}
                className={`mt-2 px-3 py-1.5 text-sm rounded-lg cursor-pointer ${
                  isManagingImages
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {isManagingImages ? 'Done' : 'Manage Images'}
              </button>

              <p className="text-sm text-gray-500 mt-1">
                {images.length} image{images.length !== 1 ? 's' : ''}
              </p>
            </div>
          ) : (
            <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
              No images
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="md:w-2/3 p-6">
          {/* Status Badge */}
          <div className="flex items-center gap-2 mb-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[product.status] || 'bg-gray-100'}`}>
              {product.status?.replaceAll('_', ' ')}
            </span>
            {missingFields.length > 0 && (
              <span className="text-sm text-red-600">
                Missing: {missingFields.join(', ')}
              </span>
            )}
          </div>

          {/* Title */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium text-gray-500">Title</label>
              {isEditing && (
                <span className={`text-sm ${(editedProduct.title?.length || 0) > 99 ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                  {editedProduct.title?.length || 0}/99
                </span>
              )}
            </div>
            {isEditing ? (
              <>
                <input
                  type="text"
                  value={editedProduct.title || ''}
                  onChange={(e) => setEditedProduct({ ...editedProduct, title: e.target.value })}
                  maxLength={150}
                  className={`w-full px-3 py-2 border rounded-lg ${
                    (editedProduct.title?.length || 0) > 99 ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {(editedProduct.title?.length || 0) > 99 && (
                  <p className="text-sm text-red-600 mt-1">⚠️ Facebook limits titles to 99 characters. Title will be truncated when posting.</p>
                )}
              </>
            ) : (
              <p className={`text-lg font-semibold ${!product.title ? 'text-red-500 italic' : ''}`}>
                {product.title || 'Missing title'}
              </p>
            )}
          </div>

          {/* Price */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-500 mb-1">Price</label>
            {isEditing ? (
              <input
                type="text"
                value={editedProduct.price || ''}
                onChange={(e) => setEditedProduct({ ...editedProduct, price: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className={`text-2xl font-bold text-green-600 ${!product.price ? 'text-red-500 italic text-lg font-normal' : ''}`}>
                {product.price || 'Missing price'}
              </p>
            )}
          </div>

          {/* Description */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
            {isEditing ? (
              <textarea
                value={editedProduct.description || ''}
                onChange={(e) => setEditedProduct({ ...editedProduct, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border rounded-lg"
              />
            ) : (
              <p className={`text-gray-700 ${!product.description ? 'text-red-500 italic' : ''}`}>
                {product.description ?
                  (product.description.length > 200
                    ? product.description.substring(0, 200) + '...'
                    : product.description)
                  : 'Missing description'
                }
              </p>
            )}
          </div>

          {/* Source Link - Opens in new tab */}
          <div className="mb-4">
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-blue-600 hover:underline text-sm"
            >
              View original product page
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>

          {/* Posting Status Message */}
          {postingStatus && (
            <div className={`mb-3 px-4 py-2 rounded-lg ${postingStatus.includes('Failed') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
              {postingStatus}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 mt-6">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 cursor-pointer"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => {
                    setEditedProduct(product)
                    setIsEditing(false)
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 cursor-pointer"
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 cursor-pointer"
                >
                  Edit
                </button>
                <button
                  onClick={handlePost}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 cursor-pointer disabled:cursor-not-allowed"
                  disabled={missingFields.length > 0 || isPosting}
                >
                  {isPosting ? 'Posting...' : 'Post to Facebook'}
                </button>
                {onDelete && (
                  <button
                    onClick={() => onDelete(product.id)}
                    className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 cursor-pointer"
                  >
                    Delete
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductCard
