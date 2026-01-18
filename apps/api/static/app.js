/**
 * PlanProof — Motivational Dashboard
 * app.js — UI Logic
 */

// ==========================================================================
// DOM Elements
// ==========================================================================
const elements = {
  // Input Form
  contextInput: document.getElementById('context-input'),
  currentTime: document.getElementById('current-time'),
  timezone: document.getElementById('timezone'),
  variant: document.getElementById('variant'),
  generateBtn: document.getElementById('generate-btn'),
  
  // Timeline
  timelineContainer: document.getElementById('timeline-container'),
  planCount: document.getElementById('plan-count'),
  
  // Status Badge
  statusBadge: document.getElementById('status-badge'),
  
  // Checklist
  checklist: document.getElementById('checklist'),
  
  // Metrics Grid (PR 1.4)
  metricsGrid: document.getElementById('metrics-grid'),
  
  // Errors
  errorsSection: document.getElementById('errors-section'),
  errorsList: document.getElementById('errors-list'),
};

// ==========================================================================
// Validation Rendering (PR 1.2)
// ==========================================================================

/**
 * Updates the status badge based on validation status.
 * @param {'pending' | 'pass' | 'fail'} status
 */
function renderStatusBadge(status) {
  const badge = elements.statusBadge;
  if (!badge) return;

  // Remove all status classes
  badge.classList.remove('status-badge--pending', 'status-badge--pass', 'status-badge--fail');

  const icon = badge.querySelector('.status-icon');
  const text = badge.querySelector('.status-text');

  switch (status) {
    case 'pass':
      badge.classList.add('status-badge--pass');
      icon.textContent = '✓';
      text.textContent = 'SYSTEM VERIFIED: FEASIBLE';
      break;
    case 'fail':
      badge.classList.add('status-badge--fail');
      icon.textContent = '✗';
      text.textContent = 'LOGISTICAL CONFLICTS DETECTED';
      break;
    case 'pending':
    default:
      badge.classList.add('status-badge--pending');
      icon.textContent = '◯';
      text.textContent = 'AWAITING PLAN';
      break;
  }
}

/**
 * Metric configuration for the pre-flight checklist.
 * Maps metric keys to display labels and pass conditions.
 */
const METRIC_CONFIG = [
  {
    key: 'constraint_violation_count',
    label: 'Constraint Violations',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
  },
  {
    key: 'overlap_minutes',
    label: 'Time Overlaps',
    format: (v) => `${v} min`,
    isPass: (v) => v === 0,
  },
  {
    key: 'hallucination_count',
    label: 'Hallucinations',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
  },
  {
    key: 'keyword_recall_score',
    label: 'Keyword Recall',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    isPass: (v) => v >= 0.7,
  },
];

/**
 * Renders the pre-flight checklist with metric values.
 * @param {Object|null} metrics - The validation.metrics object from API response
 */
function renderChecklist(metrics) {
  const checklist = elements.checklist;
  if (!checklist) return;

  // Clear existing items
  checklist.innerHTML = '';

  METRIC_CONFIG.forEach((config) => {
    const li = document.createElement('li');
    li.className = 'checklist-item';

    // Determine state
    const value = metrics ? metrics[config.key] : null;
    const hasValue = value !== null && value !== undefined;
    const passes = hasValue && config.isPass(value);

    // Set state class
    if (!hasValue) {
      li.classList.add('checklist-item--pending');
    } else if (passes) {
      li.classList.add('checklist-item--pass');
    } else {
      li.classList.add('checklist-item--fail');
    }

    // Build inner HTML
    const icon = !hasValue ? '○' : passes ? '✓' : '✗';
    const displayValue = hasValue ? config.format(value) : '—';

    li.innerHTML = `
      <span class="check-icon">${icon}</span>
      <span class="check-label">${config.label}</span>
      <span class="check-value mono">${displayValue}</span>
    `;

    checklist.appendChild(li);
  });
}

/**
 * Renders the errors list in the sidebar.
 * @param {string[]} errors - Array of error messages
 */
function renderErrors(errors) {
  const section = elements.errorsSection;
  const list = elements.errorsList;
  if (!section || !list) return;

  // Clear existing errors
  list.innerHTML = '';

  if (!errors || errors.length === 0) {
    section.classList.add('errors-section--hidden');
    return;
  }

  // Show section and populate errors
  section.classList.remove('errors-section--hidden');

  errors.forEach((error) => {
    const li = document.createElement('li');
    li.className = 'error-item';
    li.textContent = error;
    list.appendChild(li);
  });
}

// ==========================================================================
// Metrics Grid Rendering (PR 1.4)
// ==========================================================================

/**
 * Metric grid tile configuration.
 * Maps metric keys to display formatting and pass conditions.
 */
const METRICS_GRID_CONFIG = [
  {
    key: 'constraint_violation_count',
    label: 'Constraint Violations',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
  },
  {
    key: 'overlap_minutes',
    label: 'Overlap (min)',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
  },
  {
    key: 'hallucination_count',
    label: 'Hallucinations',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
  },
  {
    key: 'keyword_recall_score',
    label: 'Keyword Recall',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    isPass: (v) => v >= 0.7,
  },
];

/**
 * Renders the metrics grid with validation metric values.
 * @param {Object|null} metrics - The validation.metrics object from API response
 */
function renderMetricsGrid(metrics) {
  const grid = elements.metricsGrid;
  if (!grid) return;

  // Clear existing tiles
  grid.innerHTML = '';

  METRICS_GRID_CONFIG.forEach((config) => {
    const tile = document.createElement('div');
    tile.className = 'metric-tile';
    tile.setAttribute('data-metric', config.key);

    // Determine state
    const value = metrics ? metrics[config.key] : null;
    const hasValue = value !== null && value !== undefined;
    const passes = hasValue && config.isPass(value);

    // Set state class
    if (hasValue) {
      tile.classList.add(passes ? 'metric-tile--pass' : 'metric-tile--fail');
    }

    // Format display value
    const displayValue = hasValue ? config.format(value) : '—';

    tile.innerHTML = `
      <span class="metric-value mono">${displayValue}</span>
      <span class="metric-label">${config.label}</span>
    `;

    grid.appendChild(tile);
  });
}

/**
 * Resets the metrics grid to initial pending state.
 */
function resetMetricsGrid() {
  renderMetricsGrid(null);
}

/**
 * Renders the full validation state (status badge, checklist, metrics grid, errors).
 * @param {Object|null} validation - The validation object from API response
 */
function renderValidation(validation) {
  if (!validation) {
    renderStatusBadge('pending');
    renderChecklist(null);
    renderMetricsGrid(null);
    renderErrors([]);
    return;
  }

  // Render status badge
  const status = validation.status === 'pass' ? 'pass' : 
                 validation.status === 'fail' ? 'fail' : 'pending';
  renderStatusBadge(status);

  // Render checklist with metrics
  renderChecklist(validation.metrics || null);

  // Render metrics grid (PR 1.4)
  renderMetricsGrid(validation.metrics || null);

  // Render errors
  renderErrors(validation.errors || []);
}

/**
 * Resets the validation UI to initial pending state.
 */
function resetValidation() {
  renderValidation(null);
}

// ==========================================================================
// Timeline Rendering (PR 1.3)
// ==========================================================================

/**
 * Formats an ISO-8601 timestamp to a human-readable time string.
 * @param {string} isoString - ISO-8601 timestamp
 * @returns {string} Formatted time (e.g., "09:30 AM")
 */
function formatTime(isoString) {
  if (!isoString) return '—';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return isoString;
  }
}

/**
 * Calculates duration in minutes between two ISO-8601 timestamps.
 * @param {string} startIso - Start time ISO-8601
 * @param {string} endIso - End time ISO-8601
 * @returns {number} Duration in minutes
 */
function calculateDuration(startIso, endIso) {
  try {
    const start = new Date(startIso);
    const end = new Date(endIso);
    return Math.round((end - start) / (1000 * 60));
  } catch {
    return 0;
  }
}

/**
 * Creates a timeline item element for a plan task.
 * @param {Object} item - Plan item with task, start_time, end_time, why
 * @param {number} index - Index of the item in the plan
 * @returns {HTMLElement} The timeline item element
 */
function createTimelineItem(item, index) {
  const div = document.createElement('div');
  div.className = 'timeline-item';
  div.setAttribute('data-index', index);

  const duration = calculateDuration(item.start_time, item.end_time);
  const startFormatted = formatTime(item.start_time);
  const endFormatted = formatTime(item.end_time);

  div.innerHTML = `
    <div class="timeline-dot"></div>
    <div class="timeline-card">
      <div class="timeline-time">
        <span class="time-start mono">${startFormatted}</span>
        <span class="time-separator">→</span>
        <span class="time-end mono">${endFormatted}</span>
        <span class="time-duration mono">(${duration} min)</span>
      </div>
      <h3 class="timeline-task">${escapeHtml(item.task)}</h3>
      ${item.why ? `<p class="timeline-why">${escapeHtml(item.why)}</p>` : ''}
    </div>
  `;

  return div;
}

/**
 * Escapes HTML special characters to prevent XSS.
 * @param {string} text - Raw text
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Renders the plan timeline with task items.
 * @param {Array|null} plan - Array of plan items from API response
 */
function renderTimeline(plan) {
  const container = elements.timelineContainer;
  const countEl = elements.planCount;
  if (!container) return;

  // Clear existing content
  container.innerHTML = '';

  if (!plan || plan.length === 0) {
    // Show empty state
    container.innerHTML = `
      <div class="timeline-empty">
        <p class="empty-message">No plan generated yet.</p>
        <p class="empty-hint">Enter your context and click "Generate Plan"</p>
      </div>
    `;
    if (countEl) countEl.textContent = '0 tasks';
    return;
  }

  // Render each plan item
  plan.forEach((item, index) => {
    const timelineItem = createTimelineItem(item, index);
    container.appendChild(timelineItem);
  });

  // Update task count
  if (countEl) {
    countEl.textContent = `${plan.length} task${plan.length !== 1 ? 's' : ''}`;
  }
}

/**
 * Resets the timeline to empty state.
 */
function resetTimeline() {
  renderTimeline(null);
}

// ==========================================================================
// API Integration (PR 1.3)
// ==========================================================================

/**
 * Generates a plan by calling the /api/plan endpoint.
 */
async function generatePlan() {
  const context = elements.contextInput?.value || '';
  const currentTime = elements.currentTime?.value || '';
  const timezone = elements.timezone?.value || 'UTC';
  const variant = elements.variant?.value || 'v1_naive';

  // Validate input
  if (!context.trim()) {
    alert('Please enter some context for your plan.');
    return;
  }

  // Build request body
  const requestBody = {
    context: context,
    current_time: currentTime ? new Date(currentTime).toISOString() : new Date().toISOString(),
    timezone: timezone,
    variant: variant,
  };

  try {
    const response = await fetch('/api/plan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Render the response
    renderTimeline(data.plan || []);
    renderValidation(data.validation || null);

  } catch (error) {
    console.error('Failed to generate plan:', error);
    alert(`Failed to generate plan: ${error.message}`);
  }
}

// ==========================================================================
// Exports for testing / future use
// ==========================================================================
window.PlanProof = {
  renderValidation,
  resetValidation,
  renderStatusBadge,
  renderChecklist,
  renderErrors,
  renderMetricsGrid,
  resetMetricsGrid,
  renderTimeline,
  resetTimeline,
  generatePlan,
  formatTime,
};

// ==========================================================================
// Initialize on DOM ready
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize with pending state
  resetValidation();
  resetTimeline();

  // Set default current time to now
  const currentTimeInput = elements.currentTime;
  if (currentTimeInput) {
    const now = new Date();
    // Format for datetime-local input (YYYY-MM-DDTHH:MM)
    const localIso = now.toISOString().slice(0, 16);
    currentTimeInput.value = localIso;
  }

  // Attach event listener to Generate button
  const generateBtn = elements.generateBtn;
  if (generateBtn) {
    generateBtn.addEventListener('click', generatePlan);
  }
});
