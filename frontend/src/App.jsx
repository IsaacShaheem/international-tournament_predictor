import { useState } from 'react'

function App() {
  const [team1, setTeam1] = useState('')
  const [team2, setTeam2] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handlePredict() {
    const firstTeam = team1.trim()
    const secondTeam = team2.trim()

    setPrediction(null)
    setError('')

    if (!firstTeam || !secondTeam) {
      setError('Please enter both team names.')
      return
    }

    setIsLoading(true)

    try {
      const url =
        `http://127.0.0.1:5050/api/predict?team1=${encodeURIComponent(firstTeam)}` +
        `&team2=${encodeURIComponent(secondTeam)}`

      const response = await fetch(url)

      if (!response.ok) {
        throw new Error('Request failed')
      }

      const data = await response.json()

      setPrediction({
        team1: firstTeam,
        team2: secondTeam,
        team1Probability: data.team1_win_probability,
        team2Probability: data.team2_win_probability,
      })
    } catch {
      setError('Prediction request failed. Make sure the Flask backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main style={styles.page}>
      <section style={styles.panel}>
        <h1 style={styles.title}>World Cup Match Predictor</h1>
        <p style={styles.subtitle}>
          Enter two international teams to estimate their win probabilities.
        </p>

        <label style={styles.label}>
          Team 1
          <input
            style={styles.input}
            type="text"
            value={team1}
            onChange={(event) => setTeam1(event.target.value)}
            placeholder="Brazil"
          />
        </label>

        <label style={styles.label}>
          Team 2
          <input
            style={styles.input}
            type="text"
            value={team2}
            onChange={(event) => setTeam2(event.target.value)}
            placeholder="France"
          />
        </label>

        <button style={styles.button} type="button" onClick={handlePredict}>
          {isLoading ? 'Predicting...' : 'Predict Match'}
        </button>

        {error && <p style={styles.error}>{error}</p>}

        {prediction && (
          <div style={styles.result}>
            <h2 style={styles.matchup}>
              {prediction.team1} vs {prediction.team2}
            </h2>
            <p style={styles.probability}>
              {prediction.team1}: {(prediction.team1Probability * 100).toFixed(2)}%
            </p>
            <p style={styles.probability}>
              {prediction.team2}: {(prediction.team2Probability * 100).toFixed(2)}%
            </p>
          </div>
        )}
      </section>
    </main>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    background: '#f4f7fb',
    color: '#172033',
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  panel: {
    width: '100%',
    maxWidth: '460px',
    padding: '28px',
    border: '1px solid #d9e2ef',
    borderRadius: '8px',
    background: '#ffffff',
    boxShadow: '0 12px 30px rgba(23, 32, 51, 0.08)',
  },
  title: {
    margin: '0 0 8px',
    fontSize: '28px',
  },
  subtitle: {
    margin: '0 0 24px',
    color: '#5d6b82',
    lineHeight: '1.5',
  },
  label: {
    display: 'block',
    marginBottom: '16px',
    fontWeight: '600',
  },
  input: {
    width: '100%',
    boxSizing: 'border-box',
    marginTop: '8px',
    padding: '11px 12px',
    border: '1px solid #b8c4d6',
    borderRadius: '6px',
    fontSize: '16px',
  },
  button: {
    width: '100%',
    padding: '12px 16px',
    border: 'none',
    borderRadius: '6px',
    background: '#1769aa',
    color: '#ffffff',
    fontSize: '16px',
    fontWeight: '700',
    cursor: 'pointer',
  },
  error: {
    margin: '16px 0 0',
    color: '#b42318',
    fontWeight: '600',
  },
  result: {
    marginTop: '24px',
    paddingTop: '20px',
    borderTop: '1px solid #d9e2ef',
  },
  matchup: {
    margin: '0 0 12px',
    fontSize: '20px',
  },
  probability: {
    margin: '8px 0',
    fontSize: '18px',
  },
}

export default App
