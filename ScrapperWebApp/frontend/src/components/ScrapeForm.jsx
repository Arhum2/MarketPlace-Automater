import { useState } from 'react'

function ScrapeForm({ onScrapeComplete, isLoading, setIsLoading, setError }) {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('')
  const [progress, setProgress] = useState(0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setIsLoading(true)
    setError(null)
    setStatus('Starting scrape...')
    setProgress(0)

    try {
      // 1. Start scrape job
      const response = await fetch(`/api/scrape?url=${encodeURIComponent(url)}`, {
        method: 'POST'
      })

      if (!response.ok) throw new Error('Failed to start scrape')

      const { job_id, product_id } = await response.json()
      setStatus('Scraping in progress...')

      // 2. Poll for completion
      let completed = false
      let attempts = 0
      const maxAttempts = 120 // 2 minutes max

      while (!completed && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        attempts++
        setProgress(Math.min((attempts / 30) * 100, 90)) // Visual progress

        const progressResponse = await fetch(`/api/progress/${job_id}`)
        const { progress: jobStatus } = await progressResponse.json()

        setStatus(`Status: ${jobStatus}`)

        if (jobStatus === 'completed') {
          completed = true
          setProgress(100)
        } else if (jobStatus === 'failed') {
          throw new Error('Scraping failed')
        }
      }

      if (!completed) throw new Error('Timeout - scraping took too long')

      // 3. Get results
      const resultResponse = await fetch(`/api/results_job/${job_id}`)
      const { result } = await resultResponse.json()

      // 4. Fetch full product data
      const productResponse = await fetch(`/api/products/${product_id}`)
      const product = await productResponse.json()

      // 5. Fetch images with their database IDs (for deletion support)
      const imagesResponse = await fetch(`/api/products/${product_id}/images`)
      const images = imagesResponse.ok ? await imagesResponse.json() : []

      setStatus('Complete!')
      onScrapeComplete({ ...product, images })
      setUrl('')

    } catch (err) {
      setError(err.message)
      setStatus('')
    } finally {
      setIsLoading(false)
      setProgress(0)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste product URL (Amazon, Wayfair, etc.)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Scraping...' : 'Scrape'}
          </button>
        </div>

        {/* Progress Bar */}
        {isLoading && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>{status}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </form>
    </div>
  )
}

export default ScrapeForm
