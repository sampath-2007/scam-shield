import Icon from './Icon.jsx'

function BrandHeader({ onHome, onHowItWorks, onCheck }) {
  return (
    <header className="site-header">
      <button className="brand-button" type="button" onClick={onHome} aria-label="Scam Shield for Elders home">
        <span className="brand-symbol">
          <Icon name="shield" size={29} />
        </span>
        <span>
          <span className="brand-name">SCAM SHIELD</span>
          <span className="brand-subtitle">FOR ELDERS</span>
        </span>
      </button>

      <nav className="header-nav" aria-label="Main navigation">
        <button className="header-link" type="button" onClick={onHome}>
          Home
        </button>
        <button className="header-link" type="button" onClick={onHowItWorks}>
          How it works
        </button>
        <button
          className="button button--primary button--compact"
          type="button"
          onClick={onCheck}
          aria-label="Check a message"
        >
          <span>Check a message</span>
          <Icon name="arrow" size={21} />
        </button>
      </nav>
    </header>
  )
}

export default BrandHeader
