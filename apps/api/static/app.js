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
  
  // Constraints Section (PR 2.1)
  constraintsSection: document.getElementById('constraints-section'),
  constraintsList: document.getElementById('constraints-list'),
  
  // Coverage Progress Bar (PR 2.2)
  coverageWidget: document.getElementById('coverage-widget'),
  coverageLabel: document.getElementById('coverage-label'),
  coverageValue: document.getElementById('coverage-value'),
  coverageBar: document.getElementById('coverage-bar'),
  
  // Repair Section (PR 2.3)
  repairSection: document.getElementById('repair-section'),
  repairStatus: document.getElementById('repair-status'),
  
  // Insights Header: Assumptions & Questions (PR 3.4 Revised)
  insightsHeader: document.getElementById('insights-header'),
  assumptionsSection: document.getElementById('assumptions-section'),
  assumptionsList: document.getElementById('assumptions-list'),
  questionsSection: document.getElementById('questions-section'),
  questionsList: document.getElementById('questions-list'),
  
  // Loading State (PR 3.1)
  timelineLoading: document.getElementById('timeline-loading'),
  loadingMessage: document.getElementById('loading-message'),
  
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
  badge.classList.remove('status-badge--pending', 'status-badge--pass', 'status-badge--fail', 'status-badge--error');

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
    case 'error':
      badge.classList.add('status-badge--error');
      icon.textContent = '⚠';
      text.textContent = 'SYSTEM ERROR';
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
 * @param {boolean} isPriority - Whether to show errors in priority/alert mode (PR 3.3)
 */
function renderErrors(errors, isPriority = false) {
  const section = elements.errorsSection;
  const list = elements.errorsList;
  if (!section || !list) return;

  // Clear existing errors
  list.innerHTML = '';
  
  // Remove priority state by default
  section.classList.remove('errors-section--priority');

  if (!errors || errors.length === 0) {
    section.classList.add('errors-section--hidden');
    return;
  }

  // Show section and populate errors
  section.classList.remove('errors-section--hidden');
  
  // Add priority styling when validation fails (PR 3.3)
  if (isPriority) {
    section.classList.add('errors-section--priority');
  }

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

// ==========================================================================
// Extracted Constraints Rendering (PR 2.1)
// ==========================================================================

/**
 * Renders the extracted constraints as tags.
 * @param {string[]|null} constraints - Array of constraint strings from extracted_metadata.detected_constraints
 */
function renderConstraints(constraints) {
  const list = elements.constraintsList;
  if (!list) return;

  // Clear existing items
  list.innerHTML = '';

  if (!constraints || constraints.length === 0) {
    // Show empty state
    const emptyItem = document.createElement('li');
    emptyItem.className = 'constraints-empty';
    emptyItem.textContent = 'No hard constraints detected.';
    list.appendChild(emptyItem);
    return;
  }

  // Render each constraint as a tag
  constraints.forEach((constraint) => {
    const li = document.createElement('li');
    li.className = 'constraint-tag';
    li.innerHTML = `
      <span class="constraint-icon">⚡</span>
      <span class="constraint-text">${escapeHtml(constraint)}</span>
    `;
    list.appendChild(li);
  });
}

/**
 * Resets the constraints list to initial empty state.
 */
function resetConstraints() {
  renderConstraints(null);
}

// ==========================================================================
// Context Coverage Progress Bar (PR 2.2)
// ==========================================================================

/**
 * Determines the coverage state based on score.
 * @param {number} score - The keyword_recall_score (0.0 to 1.0)
 * @returns {'fail' | 'warning' | 'pass'} The coverage state
 */
function getCoverageState(score) {
  if (score >= 0.7) return 'pass';
  if (score >= 0.5) return 'warning';
  return 'fail';
}

/**
 * Renders the context coverage progress bar.
 * @param {number|null} score - The keyword_recall_score from validation.metrics (0.0 to 1.0)
 */
function renderCoverage(score) {
  const label = elements.coverageLabel;
  const value = elements.coverageValue;
  const bar = elements.coverageBar;
  
  if (!label || !value || !bar) return;

  // Handle null/missing score - show pending state
  if (score === null || score === undefined) {
    label.textContent = 'Calculating...';
    label.classList.add('coverage-label--pending');
    value.textContent = '—';
    value.className = 'coverage-value mono';
    bar.style.width = '0%';
    bar.className = 'coverage-bar';
    return;
  }

  // Clamp score between 0 and 1
  const clampedScore = Math.max(0, Math.min(1, score));
  const percentage = Math.round(clampedScore * 100);
  const state = getCoverageState(clampedScore);

  // Update label
  label.textContent = 'Context Coverage';
  label.classList.remove('coverage-label--pending');

  // Update value with state color
  value.textContent = `${percentage}%`;
  value.className = `coverage-value mono coverage-value--${state}`;

  // Update bar with animation
  bar.style.width = `${percentage}%`;
  bar.className = `coverage-bar coverage-bar--${state}`;
}

/**
 * Resets the coverage widget to initial pending state.
 */
function resetCoverage() {
  renderCoverage(null);
}

// ==========================================================================
// Repair Attempt Display (PR 2.3)
// ==========================================================================

/**
 * Renders the repair attempt log section.
 * Only shows if repair was attempted.
 * @param {Object|null} debug - The debug object from API response
 */
function renderRepairLog(debug) {
  const section = elements.repairSection;
  const statusEl = elements.repairStatus;
  
  if (!section || !statusEl) return;

  // Hide if no debug info or repair wasn't attempted
  if (!debug || !debug.repair_attempted) {
    section.classList.add('repair-section--hidden');
    return;
  }

  // Show section
  section.classList.remove('repair-section--hidden');

  // Update status text and styling
  if (debug.repair_success) {
    statusEl.textContent = 'Success';
    statusEl.className = 'repair-status repair-status--success';
  } else {
    statusEl.textContent = 'Failed';
    statusEl.className = 'repair-status repair-status--fail';
  }
}

/**
 * Resets the repair log to hidden state.
 */
function resetRepairLog() {
  const section = elements.repairSection;
  if (section) {
    section.classList.add('repair-section--hidden');
  }
}

// ==========================================================================
// Assumptions & Questions Rendering (PR 3.4)
// ==========================================================================

/**
 * Updates the visibility of the insights header based on whether
 * assumptions or questions are visible.
 */
function updateInsightsHeaderVisibility() {
  const header = elements.insightsHeader;
  const assumptions = elements.assumptionsSection;
  const questions = elements.questionsSection;
  
  if (!header) return;
  
  const assumptionsVisible = assumptions && !assumptions.classList.contains('insight-callout--hidden');
  const questionsVisible = questions && !questions.classList.contains('insight-callout--hidden');
  
  if (assumptionsVisible || questionsVisible) {
    header.classList.remove('insights-header--hidden');
  } else {
    header.classList.add('insights-header--hidden');
  }
}

/**
 * Renders the assumptions list as insight callout items.
 * Hides section if array is empty (defensive rendering).
 * @param {string[]|null} assumptions - Array of assumption strings
 */
function renderAssumptions(assumptions) {
  const section = elements.assumptionsSection;
  const list = elements.assumptionsList;
  if (!section || !list) return;

  // Clear existing items
  list.innerHTML = '';

  // Hide if empty or null
  if (!assumptions || assumptions.length === 0) {
    section.classList.add('insight-callout--hidden');
    updateInsightsHeaderVisibility();
    return;
  }

  // Show section and render items
  section.classList.remove('insight-callout--hidden');

  assumptions.forEach((assumption) => {
    const li = document.createElement('li');
    li.className = 'callout-item';
    li.textContent = assumption;
    list.appendChild(li);
  });
  
  updateInsightsHeaderVisibility();
}

/**
 * Renders the questions list as insight callout items.
 * Hides section if array is empty (defensive rendering).
 * @param {string[]|null} questions - Array of question strings
 */
function renderQuestions(questions) {
  const section = elements.questionsSection;
  const list = elements.questionsList;
  if (!section || !list) return;

  // Clear existing items
  list.innerHTML = '';

  // Hide if empty or null
  if (!questions || questions.length === 0) {
    section.classList.add('insight-callout--hidden');
    updateInsightsHeaderVisibility();
    return;
  }

  // Show section and render items
  section.classList.remove('insight-callout--hidden');

  questions.forEach((question) => {
    const li = document.createElement('li');
    li.className = 'callout-item';
    li.textContent = question;
    list.appendChild(li);
  });
  
  updateInsightsHeaderVisibility();
}

/**
 * Resets both assumptions and questions to hidden state.
 */
function resetInsights() {
  renderAssumptions(null);
  renderQuestions(null);
}

/**
 * Renders the full validation state (status badge, checklist, metrics grid, coverage, errors).
 * @param {Object|null} validation - The validation object from API response
 */
function renderValidation(validation) {
  if (!validation) {
    renderStatusBadge('pending');
    renderChecklist(null);
    renderMetricsGrid(null);
    renderCoverage(null);
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

  // Render coverage progress bar (PR 2.2)
  const recallScore = validation.metrics?.keyword_recall_score ?? null;
  renderCoverage(recallScore);

  // Render errors with priority highlighting if failed (PR 3.3)
  const isFailed = status === 'fail';
  renderErrors(validation.errors || [], isFailed);
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

  // Defensive: handle missing or malformed item (PR 3.2)
  if (!item || typeof item !== 'object') {
    div.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="timeline-card timeline-card--error">
        <p class="timeline-task">Invalid task data at position ${index + 1}</p>
      </div>
    `;
    return div;
  }

  const taskName = item.task || 'Untitled Task';
  const startTime = item.start_time || null;
  const endTime = item.end_time || null;
  const duration = (startTime && endTime) ? calculateDuration(startTime, endTime) : 0;
  const startFormatted = formatTime(startTime);
  const endFormatted = formatTime(endTime);
  
  // Human feasibility warning (PR 3.3) - advisory, not a hard fail
  const feasibilityFlag = item.human_feasibility_flag || null;
  const warningHtml = feasibilityFlag ? `
    <div class="timeline-warning">
      <span class="warning-icon">⚠️</span>
      <span class="warning-text">${escapeHtml(feasibilityFlag)}</span>
    </div>
  ` : '';

  div.innerHTML = `
    <div class="timeline-dot"></div>
    <div class="timeline-card">
      <div class="timeline-time">
        <span class="time-start mono">${startFormatted}</span>
        <span class="time-separator">→</span>
        <span class="time-end mono">${endFormatted}</span>
        <span class="time-duration mono">(${duration} min)</span>
      </div>
      <h3 class="timeline-task">${escapeHtml(taskName)}</h3>
      ${item.why ? `<p class="timeline-why">${escapeHtml(item.why)}</p>` : ''}
      ${warningHtml}
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
 * @param {boolean} isRejected - Whether the plan failed validation (PR 3.3)
 */
function renderTimeline(plan, isRejected = false) {
  const container = elements.timelineContainer;
  const countEl = elements.planCount;
  if (!container) return;

  // Clear existing content but preserve watermark structure
  container.innerHTML = '';
  
  // Add rejected watermark (always present, visibility controlled by CSS)
  const watermark = document.createElement('div');
  watermark.className = 'rejected-watermark';
  watermark.textContent = 'REJECTED';
  container.appendChild(watermark);
  
  // Apply or remove rejected state (PR 3.3)
  if (isRejected) {
    container.classList.add('timeline--rejected');
  } else {
    container.classList.remove('timeline--rejected');
  }

  if (!plan || plan.length === 0) {
    // Show empty state
    const emptyDiv = document.createElement('div');
    emptyDiv.className = 'timeline-empty';
    emptyDiv.innerHTML = `
      <p class="empty-message">No plan generated yet.</p>
      <p class="empty-hint">Enter your context and click "Generate Plan"</p>
    `;
    container.appendChild(emptyDiv);
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
    const isSingle = plan.length === 1;
    if (isRejected) {
      countEl.textContent = `${plan.length} ${isSingle ? 'draft task' : 'draft tasks'}`;
    } else {
      countEl.textContent = `${plan.length} ${isSingle ? 'task' : 'tasks'}`;
    }
  }
}

/**
 * Resets the timeline to empty state.
 */
function resetTimeline() {
  renderTimeline(null);
}

// ==========================================================================
// Loading State Management (PR 3.1)
// ==========================================================================

const LOADING_MESSAGES = [
  'Applying deterministic guardrails...',
  'Scanning for temporal conflicts...',
  'Verifying constraint adherence...',
  'Analyzing logical dependencies...',
  'Cross-referencing keywords...',
];

let loadingMessageInterval = null;

/**
 * Shows the loading state: disable button, show spinner, cycle messages.
 */
function showLoadingState() {
  const btn = elements.generateBtn;
  if (btn) {
    btn.disabled = true;
    btn.classList.add('btn--loading');
    btn.dataset.originalText = btn.textContent;
    btn.textContent = 'Analyzing Context...';
  }
  
  // Show loading spinner in timeline
  const loading = elements.timelineLoading;
  const empty = document.querySelector('.timeline-empty');
  if (loading) loading.classList.add('timeline-loading--active');
  if (empty) empty.style.display = 'none';
  
  // Clear existing timeline items
  const container = elements.timelineContainer;
  if (container) {
    const items = container.querySelectorAll('.timeline-item');
    items.forEach(item => item.remove());
  }
  
  // Cycle through loading messages
  let msgIndex = 0;
  if (elements.loadingMessage) {
    elements.loadingMessage.textContent = LOADING_MESSAGES[0];
    loadingMessageInterval = setInterval(() => {
      msgIndex = (msgIndex + 1) % LOADING_MESSAGES.length;
      elements.loadingMessage.textContent = LOADING_MESSAGES[msgIndex];
    }, 2000);
  }
}

/**
 * Hides the loading state: re-enable button, hide spinner.
 */
function hideLoadingState() {
  const btn = elements.generateBtn;
  if (btn) {
    btn.disabled = false;
    btn.classList.remove('btn--loading');
    btn.textContent = btn.dataset.originalText || 'Generate Plan';
  }
  
  // Hide loading spinner
  const loading = elements.timelineLoading;
  if (loading) loading.classList.remove('timeline-loading--active');
  
  // Clear message cycling
  if (loadingMessageInterval) {
    clearInterval(loadingMessageInterval);
    loadingMessageInterval = null;
  }
}

// ==========================================================================
// API Error Display (PR 3.2)
// ==========================================================================

/**
 * Displays a user-friendly API error in the sidebar.
 * @param {string} message - Error message to display
 */
function renderApiError(message) {
  // Set status badge to error state
  renderStatusBadge('error');
  
  // Reset other sections to clean state
  renderChecklist(null);
  renderMetricsGrid(null);
  renderCoverage(null);
  renderConstraints([]);
  renderRepairLog(null);
  
  // Show error in errors section
  const friendlyMessage = message.includes('500') 
    ? 'The planning service encountered an internal error. Please try again later.'
    : message.includes('404')
    ? 'The planning service is not available. Please check your connection.'
    : message.includes('NetworkError') || message.includes('fetch')
    ? 'Unable to reach the planning service. Please check your internet connection.'
    : `Planning failed: ${message}`;
  
  renderErrors([friendlyMessage]);
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

  // Show loading state (PR 3.1)
  showLoadingState();

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

    // Determine if plan is rejected (PR 3.3)
    const isRejected = data.validation?.status === 'fail';
    
    // Render the response
    renderTimeline(data.plan || [], isRejected);
    renderValidation(data.validation || null);
    
    // Render extracted metadata (PR 2.1)
    const constraints = data.extracted_metadata?.detected_constraints || [];
    renderConstraints(constraints);
    
    // Render repair log (PR 2.3)
    renderRepairLog(data.debug || null);
    
    // Render assumptions & questions (PR 3.4)
    renderAssumptions(data.assumptions || null);
    renderQuestions(data.questions || null);
    
    // Hide loading state (PR 3.1)
    hideLoadingState();

  } catch (error) {
    console.error('Failed to generate plan:', error);
    hideLoadingState();
    
    // Show friendly error in sidebar (PR 3.2)
    renderApiError(error.message);
    
    // Reset timeline to empty state
    resetTimeline();
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
  renderConstraints,
  resetConstraints,
  renderCoverage,
  resetCoverage,
  renderRepairLog,
  resetRepairLog,
  renderAssumptions,
  renderQuestions,
  resetInsights,
  renderTimeline,
  resetTimeline,
  showLoadingState,
  hideLoadingState,
  renderApiError,
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
  resetConstraints();
  resetCoverage();
  resetRepairLog();
  resetInsights();

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
