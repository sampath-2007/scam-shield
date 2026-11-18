import { useState } from 'react'
import { MAX_MESSAGE_LENGTH, SAMPLE_MESSAGES } from '../copy.js'
import Icon from './Icon.jsx'

function CheckerScreen({
  language,
  copy,
  message,
  error,
  isLoading,
  onMessageChange,
  onLanguageChange,
  onSample,
  onSubmit,
}) {
  const [clipboardError, setClipboardError] = useState('')

  function updateMessage(value) {
    setClipboardError('')
    onMessageChange(value)
  }

  async function pasteFromClipboard() {
    setClipboardError('')
    if (!navigator.clipboard?.readText) {
      setClipboardError(copy.clipboardError)
      return
    }

    try {
      const clipboardText = await navigator.clipboard.readText()
      if (!clipboardText) {
        setClipboardError(copy.clipboardEmpty)
      } else if (clipboardText.length > MAX_MESSAGE_LENGTH) {
        setClipboardError(copy.clipboardTooLong)
      } else {
        updateMessage(clipboardText)
      }
    } catch {
      setClipboardError(copy.clipboardError)
    }
  }

  const remainingCharacters = Math.max(0, MAX_MESSAGE_LENGTH - message.length)

  return (
    <section className="checker-layout">
      <div className="page-intro">
        <p className="eyebrow">
          <span className="eyebrow-dot" />
          {copy.checkerEyebrow}
        </p>
        <h1 className="page-title">{copy.checkerTitle}</h1>
        <p className="page-description">{copy.checkerDescription}</p>
      </div>

      <div className="checker-columns">
        <form className="surface-card checker-card" onSubmit={onSubmit} noValidate>
          <label className="field-label" htmlFor="message-text">
            {copy.messageLabel}
          </label>
          <textarea
            id="message-text"
            className="message-input"
            value={message}
            onChange={(event) => updateMessage(event.target.value)}
            placeholder={copy.placeholder}
            maxLength={MAX_MESSAGE_LENGTH}
            aria-describedby="message-count"
            disabled={isLoading}
          />
          <div className="input-toolbar">
            <span className="character-count" id="message-count" aria-live="polite">
              {copy.remaining.replace('{count}', remainingCharacters.toLocaleString())}
            </span>
            <button
              className="text-button"
              type="button"
              onClick={pasteFromClipboard}
              disabled={isLoading}
            >
              <Icon name="paste" size={22} />
              {copy.pasteButton}
            </button>
          </div>

          <p className="sample-label">{copy.samplesLabel}</p>
          <div className="sample-list">
            <button
              className="sample-button"
              type="button"
              onClick={() => {
                setClipboardError('')
                onSample(SAMPLE_MESSAGES.scam)
              }}
              disabled={isLoading}
            >
              <span className="sample-dot text-scam" />
              {copy.sampleScam}
            </button>
            <button
              className="sample-button"
              type="button"
              onClick={() => {
                setClipboardError('')
                onSample(SAMPLE_MESSAGES.suspicious)
              }}
              disabled={isLoading}
            >
              <span className="sample-dot text-suspicious" />
              {copy.sampleSuspicious}
            </button>
            <button
              className="sample-button"
              type="button"
              onClick={() => {
                setClipboardError('')
                onSample(SAMPLE_MESSAGES.safe)
              }}
              disabled={isLoading}
            >
              <span className="sample-dot text-safe" />
              {copy.sampleSafe}
            </button>
          </div>

          <div className="form-bottom">
            <div className="language-field">
              <label className="field-label" htmlFor="explanation-language">
                {copy.languageLabel}
              </label>
              <select
                id="explanation-language"
                className="language-select"
                value={language}
                onChange={(event) => onLanguageChange(event.target.value)}
                disabled={isLoading}
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी</option>
                <option value="kn">ಕನ್ನಡ</option>
              </select>
            </div>
            <button className="button button--primary analyze-button" type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <span className="loading-spinner" aria-hidden="true" />
                  {copy.loadingButton}
                </>
              ) : (
                <>
                  {copy.submitButton}
                  <Icon name="arrow" size={22} />
                </>
              )}
            </button>
          </div>

          {(error || clipboardError) && (
            <p className="form-error" role="alert">
              {error || clipboardError}
            </p>
          )}
        </form>

        <aside className="surface-card privacy-card">
          <span className="privacy-card-icon">
            <Icon name="lock" size={27} />
          </span>
          <h2>{copy.privacyTitle}</h2>
          <p>{copy.privacyDescription}</p>
          <ul className="privacy-list">
            <li>
              <Icon name="check" size={20} />
              {copy.privacyTipOne}
            </li>
            <li>
              <Icon name="check" size={20} />
              {copy.privacyTipTwo}
            </li>
            <li>
              <Icon name="check" size={20} />
              {copy.privacyTipThree}
            </li>
          </ul>
        </aside>
      </div>
    </section>
  )
}

export default CheckerScreen
