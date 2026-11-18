import Icon from './Icon.jsx'

const features = [
  {
    icon: 'scan',
    title: 'Scam detection',
    description:
      'Look for common warning signs in SMS and WhatsApp messages before you act.',
  },
  {
    icon: 'spark',
    title: 'Simple explanations',
    description:
      'Understand the result in clear English, हिन्दी, or ಕನ್ನಡ.',
  },
  {
    icon: 'heart',
    title: 'Family safety',
    description:
      'A calm second opinion to help you pause and make a confident choice.',
  },
]

function HomeScreen({ onStart }) {
  return (
    <>
      <section className="home-hero">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="eyebrow-dot" />
            A calmer way to stay alert
          </p>
          <h1 className="hero-title">Stay Safe from Online Scams</h1>
          <p className="hero-description">
            A simple second opinion for SMS and WhatsApp messages. Check for
            common warning signs before you reply, tap a link, or send money.
          </p>
          <div className="hero-actions">
            <button className="button button--primary" type="button" onClick={onStart}>
              Check a Message
              <Icon name="arrow" size={23} />
            </button>
            <span className="privacy-note">
              <Icon name="lock" size={22} />
              Your message is not saved
            </span>
          </div>
        </div>

        <div
          className="hero-art"
          role="img"
          aria-label="A glowing shield representing online safety"
        >
          <div className="hero-orbit" />
          <span className="orbit-spark orbit-spark--one" />
          <span className="orbit-spark orbit-spark--two" />
          <span className="orbit-spark orbit-spark--three" />
          <div className="shield-illustration">
            <Icon name="shield" size={104} />
          </div>
          <div className="art-note">
            <span className="art-note-icon">
              <Icon name="check" size={25} />
            </span>
            <span>
              <strong>Pause. Check. Decide.</strong>
              <span>A little more confidence online</span>
            </span>
          </div>
        </div>
      </section>

      <section className="features-section" id="how-it-works">
        <div className="section-heading">
          <p className="eyebrow">
            <span className="eyebrow-dot" />
            Made for everyday peace of mind
          </p>
          <h2>Clear help, without the worry</h2>
          <p>A simple check can help you pause and decide what to do next.</p>
        </div>
        <div className="feature-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.title}>
              <span className="feature-icon">
                <Icon name={feature.icon} size={27} />
              </span>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  )
}

export default HomeScreen
