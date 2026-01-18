/**
 * PlanProof — Motivational Dashboard
 * app.js — UI Logic
 */

// ==========================================================================
// DOM Elements
// ==========================================================================
const elements = {
  // Status Badge
  statusBadge: document.getElementById('status-badge'),
  
  // Checklist
  checklist: document.getElementById('checklist'),
  
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
  {
    key: 'human_feasibility_flags',
    label: 'Human Feasibility',
    format: (v) => v.toString(),
    isPass: (v) => v === 0,
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

/**
 * Renders the full validation state (status badge, checklist, errors).
 * @param {Object|null} validation - The validation object from API response
 */
function renderValidation(validation) {
  if (!validation) {
    renderStatusBadge('pending');
    renderChecklist(null);
    renderErrors([]);
    return;
  }

  // Render status badge
  const status = validation.status === 'pass' ? 'pass' : 
                 validation.status === 'fail' ? 'fail' : 'pending';
  renderStatusBadge(status);

  // Render checklist with metrics
  renderChecklist(validation.metrics || null);

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
// Exports for testing / future use
// ==========================================================================
window.PlanProof = {
  renderValidation,
  resetValidation,
  renderStatusBadge,
  renderChecklist,
  renderErrors,
};

// ==========================================================================
// Initialize on DOM ready
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize with pending state
  resetValidation();
});
