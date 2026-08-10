const pwInput = document.getElementById('pwInput');
const toggleBtn = document.getElementById('toggleVisibility');
const idleState = document.getElementById('idleState');
const resultsState = document.getElementById('resultsState');
const errorState = document.getElementById('errorState');
const modelBadge = document.getElementById('modelBadge');
const modelBadgeText = document.getElementById('modelBadgeText');

let debounceTimer = null;

// Map API strength labels to CSS-friendly level keys + progress %
const LEVEL_MAP = {
  'very weak':   { key: 'very-weak',   pct: 12 },
  'weak':        { key: 'weak',        pct: 30 },
  'fair':        { key: 'fair',        pct: 55 },
  'medium':      { key: 'fair',        pct: 55 },
  'strong':      { key: 'strong',      pct: 80 },
  'very strong': { key: 'very-strong', pct: 100 },
};

function levelFor(label) {
  const norm = String(label).toLowerCase().trim();
  return LEVEL_MAP[norm] || { key: 'fair', pct: 50 };
}

toggleBtn.addEventListener('click', () => {
  pwInput.type = pwInput.type === 'password' ? 'text' : 'password';
});

pwInput.addEventListener('input', () => {
  const value = pwInput.value;
  clearTimeout(debounceTimer);

  if (!value) {
    showIdle();
    return;
  }

  debounceTimer = setTimeout(() => analyze(value), 150);
});

async function analyze(password) {
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || 'Something went wrong.');
      return;
    }

    renderResults(password, data);
  } catch (err) {
    showError('Could not reach the analysis server.');
  }
}

function showIdle() {
  idleState.hidden = false;
  resultsState.hidden = true;
  errorState.hidden = true;
}

function showError(message) {
  idleState.hidden = true;
  resultsState.hidden = true;
  errorState.hidden = false;
  errorState.textContent = message;
}

function renderResults(password, data) {
  idleState.hidden = true;
  errorState.hidden = true;
  resultsState.hidden = false;

  const level = levelFor(data.strength);
  resultsState.dataset.level = level.key;

  document.getElementById('strengthValue').textContent = data.strength;
  document.getElementById('meterFill').style.width = level.pct + '%';
  document.getElementById('strengthSource').textContent = data.using_ml_model
    ? 'via trained ML model'
    : 'via heuristic (no trained model loaded)';

  document.getElementById('entropyValue').innerHTML =
    data.entropy.toFixed(2) + ' <span class="unit">bits</span>';
  document.getElementById('crackValue').textContent = data.crack_time;

  document.getElementById('valLength').textContent = data.analysis['Length'];
  document.getElementById('valUpper').textContent = data.analysis['Uppercase'];
  document.getElementById('valLower').textContent = data.analysis['Lowercase'];
  document.getElementById('valDigits').textContent = data.analysis['Digits'];
  document.getElementById('valSpecial').textContent = data.analysis['Special Characters'];

  // Pin tumblers: length>=12, upper, lower, digit, special
  const pins = {
    length: data.analysis['Length'] >= 12,
    upper: data.analysis['Uppercase'] > 0,
    lower: data.analysis['Lowercase'] > 0,
    digit: data.analysis['Digits'] > 0,
    special: data.analysis['Special Characters'] > 0,
  };

  let setCount = 0;
  document.querySelectorAll('.pin').forEach((pinEl) => {
    const key = pinEl.dataset.pin;
    const isSet = pins[key];
    pinEl.classList.toggle('pin--set', isSet);
    if (isSet) setCount++;
  });
  document.getElementById('tumblerCaption').textContent = `${setCount} / 5 conditions met`;

  // Suggestions
  const list = document.getElementById('suggestionsList');
  list.innerHTML = '';
  const suggestionsBlock = document.getElementById('suggestionsBlock');

  if (data.suggestions.length === 0) {
    list.classList.add('suggestions__list--clean');
    const li = document.createElement('li');
    li.textContent = 'No basic improvements detected.';
    list.appendChild(li);
  } else {
    list.classList.remove('suggestions__list--clean');
    data.suggestions.forEach((s) => {
      const li = document.createElement('li');
      li.textContent = s;
      list.appendChild(li);
    });
  }
  suggestionsBlock.hidden = false;
}

// Model badge, set from server-rendered flag
(function initModelBadge() {
  const usingMl = document.body.dataset.usingMl === 'true';
  modelBadge.dataset.state = usingMl ? 'ml' : 'heuristic';
  modelBadgeText.textContent = usingMl ? 'ml model active' : 'heuristic mode';
})();