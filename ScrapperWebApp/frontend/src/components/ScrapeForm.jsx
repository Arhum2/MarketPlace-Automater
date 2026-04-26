import { useState, useRef } from 'react'

function ScrapeForm({ onScrapeComplete, isLoading, setIsLoading, setError }) {
  const [urls, setUrls] = useState([''])
  const [statuses, setStatuses] = useState({}) // index → { state: 'scraping'|'done'|'failed', message: '' }
  const inputRefs = useRef([])

  const setStatus = (index, state, message = '') =>
    setStatuses(prev => ({ ...prev, [index]: { state, message } }))

  const addUrl = () => {
    setUrls(prev => {
      const next = [...prev, '']
      setTimeout(() => inputRefs.current[next.length - 1]?.focus(), 0)
      return next
    })
  }

  const removeUrl = (index) => {
    setUrls(prev => prev.filter((_, i) => i !== index))
    setStatuses(prev => {
      const next = { ...prev }
      delete next[index]
      return next
    })
  }

  const updateUrl = (index, value) =>
    setUrls(prev => prev.map((u, i) => i === index ? value : u))

  const handleKeyDown = (e, index) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addUrl()
    }
  }

  const scrapeOne = async (url, index) => {
    setStatus(index, 'scraping')

    let response = await fetch(`/api/scrape?url=${encodeURIComponent(url)}`, { method: 'POST' })

    if (response.status === 409) {
      const { existing_product_id } = await response.json()
      const overwrite = window.confirm(`"${url}" was already scraped. Overwrite it?`)
      if (!overwrite) {
        setStatus(index, 'idle')
        return
      }
      await fetch(`/api/products/${existing_product_id}`, { method: 'DELETE' })
      response = await fetch(`/api/scrape?url=${encodeURIComponent(url)}`, { method: 'POST' })
    }

    if (!response.ok) throw new Error('Failed to start scrape')

    const { job_id, product_id } = await response.json()

    let completed = false
    let attempts = 0
    const maxAttempts = 120

    while (!completed && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      attempts++

      const progressResponse = await fetch(`/api/progress/${job_id}`)
      const { progress: jobStatus } = await progressResponse.json()

      if (jobStatus === 'completed') {
        completed = true
      } else if (jobStatus === 'failed') {
        throw new Error('Scraping failed')
      }
    }

    if (!completed) throw new Error('Timed out')

    const productResponse = await fetch(`/api/products/${product_id}`)
    const product = await productResponse.json()

    const imagesResponse = await fetch(`/api/products/${product_id}/images`)
    const images = imagesResponse.ok ? await imagesResponse.json() : []

    onScrapeComplete({ ...product, images })
    setStatus(index, 'done')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const nonEmpty = urls.map((url, index) => ({ url: url.trim(), index })).filter(({ url }) => url)
    if (!nonEmpty.length) return

    setIsLoading(true)
    setError(null)

    const results = await Promise.allSettled(
      nonEmpty.map(({ url, index }) =>
        scrapeOne(url, index).catch(err => {
          setStatus(index, 'failed', err.message)
          throw err
        })
      )
    )

    // Clear successful URLs, keep failed ones
    const failedIndexes = new Set(
      nonEmpty.filter((_, i) => results[i].status === 'rejected').map(({ index }) => index)
    )
    setUrls(prev => {
      const kept = prev.filter((_, i) => failedIndexes.has(i))
      return kept.length ? kept : ['']
    })
    setStatuses(prev => {
      const next = {}
      let newIndex = 0
      urls.forEach((_, i) => {
        if (failedIndexes.has(i)) next[newIndex++] = prev[i]
      })
      return next
    })

    setIsLoading(false)
  }

  const hasUrls = urls.some(u => u.trim())

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col gap-2">
          {urls.map((url, index) => {
            const s = statuses[index]
            return (
              <div key={index} className="flex gap-2 items-center">
                <input
                  ref={el => inputRefs.current[index] = el}
                  type="url"
                  value={url}
                  onChange={(e) => updateUrl(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  placeholder="Paste product URL (Amazon, Wayfair, etc.)"
                  className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    s?.state === 'failed' ? 'border-red-400 bg-red-50' :
                    s?.state === 'done' ? 'border-green-400 bg-green-50' :
                    'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {s?.state === 'scraping' && (
                  <span className="text-sm text-blue-500 whitespace-nowrap">Scraping...</span>
                )}
                {s?.state === 'done' && (
                  <span className="text-sm text-green-600 whitespace-nowrap">Done</span>
                )}
                {s?.state === 'failed' && (
                  <span className="text-sm text-red-600 whitespace-nowrap">Failed</span>
                )}
                {urls.length > 1 && !isLoading && (
                  <button
                    type="button"
                    onClick={() => removeUrl(index)}
                    className="text-gray-400 hover:text-red-500 px-1 text-lg leading-none"
                  >
                    ×
                  </button>
                )}
              </div>
            )
          })}
        </div>

        <div className="flex gap-3 mt-3">
          <button
            type="button"
            onClick={addUrl}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed text-sm"
          >
            + Add URL
          </button>
          <button
            type="submit"
            disabled={isLoading || !hasUrls}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Scraping...' : urls.filter(u => u.trim()).length > 1 ? 'Scrape All' : 'Scrape'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ScrapeForm
