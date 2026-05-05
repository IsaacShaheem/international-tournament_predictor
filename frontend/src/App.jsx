import { useState } from 'react'

function App() {
  const [view, setView] = useState('menu')

  const [team1, setTeam1] = useState('')
  const [team2, setTeam2] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const [groups, setGroups] = useState([])
  const [totalAdvancingTeams, setTotalAdvancingTeams] = useState('8')
  const [seedValue, setSeedValue] = useState('')
  const [fullSimulationResults, setFullSimulationResults] = useState([])
  const [fullSimulationError, setFullSimulationError] = useState('')
  const [isFullSimulationLoading, setIsFullSimulationLoading] = useState(false)

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

  function handleGenerateGroups() {
    setGroups([
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', ''],
    ])
    setFullSimulationResults([])
    setFullSimulationError('')
    setView('groups')
  }

  function isPowerOfTwo(number) {
    return number > 0 && (number & (number - 1)) === 0
  }

  function handleGroupInputChange(groupIndex, teamIndex, value) {
    const updatedGroups = [...groups]
    const updatedGroup = [...updatedGroups[groupIndex]]

    updatedGroup[teamIndex] = value
    updatedGroups[groupIndex] = updatedGroup

    setGroups(updatedGroups)
  }

  function validateGroups() {
    const seenTeams = new Set()

    for (const group of groups) {
      for (const team of group) {
        const cleanedTeam = team.trim()

        if (!cleanedTeam) {
          return 'Please enter every team name before running the simulation.'
        }

        const normalizedTeam = cleanedTeam.toLowerCase()

        if (seenTeams.has(normalizedTeam)) {
          return 'Please remove duplicate team names before running the simulation.'
        }

        seenTeams.add(normalizedTeam)
      }
    }

    return ''
  }

  function validateSimulationSettings() {
    const cleanedTotalAdvancingTeams = totalAdvancingTeams.trim()

    if (!cleanedTotalAdvancingTeams) {
      return 'Please enter the number of advancing teams.'
    }

    const parsedTotalAdvancingTeams = Number(cleanedTotalAdvancingTeams)

    if (!Number.isInteger(parsedTotalAdvancingTeams)) {
      return 'Total advancing teams must be an integer.'
    }

    if (!isPowerOfTwo(parsedTotalAdvancingTeams)) {
      return 'Total advancing teams must be a power of 2.'
    }

    const baseQualifiers = groups.length * 2
    const maxQualifiers = baseQualifiers + groups.length

    if (parsedTotalAdvancingTeams < baseQualifiers) {
      return `Total advancing teams must be at least ${baseQualifiers}.`
    }

    if (parsedTotalAdvancingTeams > maxQualifiers) {
      return `Total advancing teams must be no more than ${maxQualifiers}.`
    }

    if (seedValue.trim()) {
      const parsedSeed = Number(seedValue.trim())

      if (!Number.isInteger(parsedSeed)) {
        return 'Seed must be an integer.'
      }
    }

    return ''
  }

  async function handleRunFullSimulation() {
    setFullSimulationError('')
    setFullSimulationResults([])

    const validationError = validateGroups() || validateSimulationSettings()

    if (validationError) {
      setFullSimulationError(validationError)
      return
    }

    setIsFullSimulationLoading(true)

    try {
      const cleanedGroups = groups.map((group) =>
        group.map((team) => team.trim()),
      )

      const requestBody = {
        groups: cleanedGroups,
        total_advancing_teams: Number(totalAdvancingTeams.trim()),
      }

      if (seedValue.trim()) {
        requestBody.seed = Number(seedValue.trim())
      }

      const response = await fetch('http://127.0.0.1:5050/api/simulate-full', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        throw new Error('Request failed')
      }

      const data = await response.json()
      const sortedResults = Object.entries(data).sort((a, b) => b[1] - a[1])

      setFullSimulationResults(sortedResults)
    } catch {
      setFullSimulationError(
        'Full simulation request failed. Make sure the Flask backend is running.',
      )
    } finally {
      setIsFullSimulationLoading(false)
    }
  }

  function renderMenuView() {
    return (
      <section>
        <h1 style={styles.title}>World Cup Prediction Engine</h1>
        <p style={styles.subtitle}>Choose a feature to explore.</p>

        <button style={styles.button} type="button" onClick={() => setView('match')}>
          Match Prediction
        </button>

        <button
          style={styles.secondaryButton}
          type="button"
          onClick={() => setView('setup')}
        >
          Tournament Simulation
        </button>
      </section>
    )
  }

  function renderMatchView() {
    return (
      <section>
        <button style={styles.backButton} type="button" onClick={() => setView('menu')}>
          Back
        </button>

        <h1 style={styles.title}>Match Prediction</h1>
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
    )
  }

  function renderSetupView() {
    return (
      <section>
        <button style={styles.backButton} type="button" onClick={() => setView('menu')}>
          Back
        </button>

        <h1 style={styles.title}>Tournament Setup</h1>
        <p style={styles.subtitle}>This simulator uses 4 groups with 4 teams each.</p>

        <div style={styles.setupBox}>
          <p style={styles.probability}>Number of groups: 4</p>
          <p style={styles.probability}>Teams per group: 4</p>
        </div>

        <button style={styles.button} type="button" onClick={handleGenerateGroups}>
          Generate Groups
        </button>
      </section>
    )
  }

  function renderGroupsView() {
    return (
      <section>
        <button style={styles.backButton} type="button" onClick={() => setView('setup')}>
          Back
        </button>

        <h1 style={styles.title}>Group Input</h1>
        <p style={styles.subtitle}>Enter 16 unique international team names.</p>

        {groups.map((group, groupIndex) => (
          <div style={styles.groupBox} key={`group-${groupIndex}`}>
            <h2 style={styles.sectionTitle}>Group {String.fromCharCode(65 + groupIndex)}</h2>

            {group.map((team, teamIndex) => (
              <label style={styles.label} key={`group-${groupIndex}-team-${teamIndex}`}>
                Team {teamIndex + 1}
                <input
                  style={styles.input}
                  type="text"
                  value={team}
                  onChange={(event) =>
                    handleGroupInputChange(groupIndex, teamIndex, event.target.value)
                  }
                  placeholder="Team name"
                />
              </label>
            ))}
          </div>
        ))}

        <label style={styles.label}>
          Total advancing teams
          <input
            style={styles.input}
            type="text"
            value={totalAdvancingTeams}
            onChange={(event) => setTotalAdvancingTeams(event.target.value)}
            placeholder="8"
          />
        </label>

        <label style={styles.label}>
          Seed (optional)
          <input
            style={styles.input}
            type="text"
            value={seedValue}
            onChange={(event) => setSeedValue(event.target.value)}
            placeholder="42"
          />
        </label>

        <button
          style={styles.button}
          type="button"
          onClick={handleRunFullSimulation}
          disabled={isFullSimulationLoading}
        >
          {isFullSimulationLoading ? 'Running Simulation...' : 'Run Full Simulation'}
        </button>

        {fullSimulationError && <p style={styles.error}>{fullSimulationError}</p>}

        {fullSimulationResults.length > 0 && (
          <div style={styles.result}>
            <h2 style={styles.matchup}>Championship Probabilities</h2>

            {fullSimulationResults.map((entry) => {
              const team = entry[0]
              const probability = entry[1]

              return (
                <p style={styles.probability} key={team}>
                  {team}: {(probability * 100).toFixed(2)}%
                </p>
              )
            })}
          </div>
        )}
      </section>
    )
  }

  return (
    <main style={styles.page}>
      <section style={styles.panel}>
        {view === 'menu' && renderMenuView()}
        {view === 'match' && renderMatchView()}
        {view === 'setup' && renderSetupView()}
        {view === 'groups' && renderGroupsView()}
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
    maxWidth: '560px',
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
  sectionTitle: {
    margin: '0 0 16px',
    fontSize: '20px',
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
    marginTop: '8px',
  },
  secondaryButton: {
    width: '100%',
    padding: '12px 16px',
    border: '1px solid #1769aa',
    borderRadius: '6px',
    background: '#ffffff',
    color: '#1769aa',
    fontSize: '16px',
    fontWeight: '700',
    cursor: 'pointer',
    marginTop: '12px',
  },
  backButton: {
    marginBottom: '20px',
    padding: '8px 12px',
    border: '1px solid #b8c4d6',
    borderRadius: '6px',
    background: '#ffffff',
    color: '#172033',
    fontSize: '14px',
    fontWeight: '700',
    cursor: 'pointer',
  },
  setupBox: {
    marginBottom: '16px',
    padding: '16px',
    border: '1px solid #d9e2ef',
    borderRadius: '8px',
    background: '#f8fafc',
  },
  groupBox: {
    marginBottom: '20px',
    paddingBottom: '4px',
    borderBottom: '1px solid #d9e2ef',
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
