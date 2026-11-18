import Icon from './Icon.jsx'

function readableCode(code) {
  return code
    .toLowerCase()
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function ResultScreen({ result, language, copy, onAnalyzeAnother, onHome }) {
  const verdictClass = result.verdict.toLowerCase()
  const verdictIcon = result.verdict === 'SAFE' ? 'shield' : 'warning'

  return (
    <section className="result-layout">
      <div className="result-heading">
        <p className="eyebrow">
          <span className="eyebrow-dot" />
          {copy.resultEyebrow}
        </p>
      </div>

      <article className={`surface-card verdict-card verdict-card--${verdictClass}`}>
        <span className="verdict-icon">
          <Icon name={verdictIcon} size={38} />
        </span>
        <div>
          <p className="verdict-label">{copy.scoreLabel}</p>
          <h1 className="verdict-name">{result.verdict}</h1>
          <p className="verdict-explanation">{result.explanation}</p>
        </div>
        <div className="score-box" aria-label={`${copy.scoreLabel}: ${result.score} out of 100`}>
          <span className="score-number">{result.score}</span>
          <span className="score-caption">/ 100</span>
        </div>
      </article>

      <div className="result-grid">
        <section className="surface-card result-panel" aria-labelledby="reasons-heading">
          <h2 id="reasons-heading">
            <Icon name="scan" size={25} />
            {copy.reasonsTitle}
          </h2>
          {result.reasons.length ? (
            <div className="reason-list">
              {result.reasons.map((reason, index) => (
                <article className="reason-item" key={`${reason.code}-${index}`}>
                  <h3>{readableCode(reason.code)}</h3>
                  <p>{reason.explanations[language] || reason.explanations.en}</p>
                  <div className="reason-weight">
                    {language === 'hi'
                      ? `जोखिम भार: ${reason.risk_weight}`
                      : language === 'kn'
                        ? `ಅಪಾಯದ ತೂಕ: ${reason.risk_weight}`
                        : `Risk weight: ${reason.risk_weight}`}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-reasons">{copy.noReasons}</p>
          )}
        </section>

        <section className="surface-card result-panel" aria-labelledby="links-heading">
          <h2 id="links-heading">
            <Icon name="link" size={25} />
            {copy.linksTitle}
          </h2>
          <p className="link-warning">{copy.linksWarning}</p>
          {result.extracted_links.length ? (
            <ul className="link-list">
              {result.extracted_links.map((link, index) => (
                <li key={`${link}-${index}`}>{link}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-reasons">{copy.noLinks}</p>
          )}
        </section>
      </div>

      <aside className="safety-advice">
        <Icon name="shield" size={27} />
        <div>
          <h2>{copy.safetyTitle}</h2>
          <p>{copy.safety[result.verdict]}</p>
        </div>
      </aside>

      <div className="result-actions">
        <button className="button button--primary" type="button" onClick={onAnalyzeAnother}>
          {copy.analyzeAnother}
          <Icon name="arrow" size={22} />
        </button>
        <button className="button button--secondary" type="button" onClick={onHome}>
          <Icon name="home" size={22} />
          {copy.returnHome}
        </button>
      </div>
    </section>
  )
}

export default ResultScreen
