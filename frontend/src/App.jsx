import { useState } from 'react'
import './App.css'
import BrandHeader from './components/BrandHeader.jsx'
import CheckerScreen from './components/CheckerScreen.jsx'
import HomeScreen from './components/HomeScreen.jsx'
import ResultScreen from './components/ResultScreen.jsx'
import { COPY, MAX_MESSAGE_LENGTH } from './copy.js'

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000')
  .replace(/\/+$/, '')
const SUPPORTED_LANGUAGES = ['en', 'hi', 'kn']
const VERDICTS = ['SCAM', 'SUSPICIOUS', 'SAFE']

function isValidResult(data, language) {
  return (
    data &&
    typeof data === 'object' &&
    VERDICTS.includes(data.verdict) &&
    Number.isInteger(data.score) &&
    data.score >= 0 &&
    data.score <= 100 &&
    Array.isArray(data.reasons) &&
    data.reasons.every(
      (reason) =>
        reason &&
        typeof reason.code === 'string' &&
        Number.isInteger(reason.risk_weight) &&
        reason.explanations &&
        SUPPORTED_LANGUAGES.every(
          (code) => typeof reason.explanations[code] === 'string',
        ),
    ) &&
    Array.isArray(data.extracted_links) &&
    data.extracted_links.every((link) => typeof link === 'string') &&
    typeof data.explanation === 'string' &&
    data.language === language
  )
}

function getApiError(data, status, copy) {
  if (status === 429) return copy.rateLimitError

  const detail = data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item?.message)
      .filter((message) => typeof message === 'string')
    if (messages.length) return messages.join(' ')
  }
  return copy.serverError
}

function App() {
  const [screen, setScreen] = useState('home')
  const [language, setLanguage] = useState('en')
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const copy = COPY[language]

  function startChecking() {
    setError('')
    setScreen('checker')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function returnHome() {
    setMessage('')
    setResult(null)
    setError('')
    setScreen('home')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function showHowItWorks() {
    setScreen('home')
    window.setTimeout(() => {
      document
        .getElementById('how-it-works')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 40)
  }

  async function checkMessage(event) {
    event.preventDefault()
    setError('')

    if (!message.trim()) {
      setError(copy.emptyError)
      return
    }
    if (message.length > MAX_MESSAGE_LENGTH) {
      setError(copy.tooLongError)
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: message.trim(), language }),
      })
      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(getApiError(data, response.status, copy))
      }
      if (!isValidResult(data, language)) {
        throw new Error(copy.invalidResponseError)
      }

      setResult(data)
      setMessage('')
      setScreen('result')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (requestError) {
      setError(
        requestError instanceof TypeError
          ? copy.networkError
          : requestError instanceof Error
            ? requestError.message
            : copy.networkError,
      )
    } finally {
      setIsLoading(false)
    }
  }

  function analyzeAnother() {
    setMessage('')
    setResult(null)
    setError('')
    setScreen('checker')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <div className="ambient-glow ambient-glow--top" aria-hidden="true" />
      <div className="ambient-glow ambient-glow--bottom" aria-hidden="true" />
      <BrandHeader
        onHome={returnHome}
        onHowItWorks={showHowItWorks}
        onCheck={startChecking}
      />

      <main className="page-content">
        {screen === 'home' && <HomeScreen onStart={startChecking} />}
        {screen === 'checker' && (
          <CheckerScreen
            language={language}
            copy={copy}
            message={message}
            error={error}
            isLoading={isLoading}
            onMessageChange={(value) => {
              setMessage(value)
              if (error) setError('')
            }}
            onLanguageChange={(value) => {
              setLanguage(value)
              setError('')
            }}
            onSample={(sample) => {
              setMessage(sample)
              setError('')
            }}
            onSubmit={checkMessage}
          />
        )}
        {screen === 'result' && result && (
          <ResultScreen
            result={result}
            language={language}
            copy={copy}
            onAnalyzeAnother={analyzeAnother}
            onHome={returnHome}
          />
        )}
      </main>

      <footer className="site-footer">
        <p>{copy.footerNote}</p>
        <span className="footer-mark">SCAM SHIELD <span>•</span> FOR ELDERS</span>
      </footer>
    </div>
  )
}

export default App
