// API Base URL - Backend server
const API_BASE = 'http://localhost:8000/api';

// Global state
let queryCount = 0;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const queryInput = document.getElementById('queryInput');
const queryButton = document.getElementById('queryButton');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const documentCount = document.getElementById('documentCount');
const queryCountElement = document.getElementById('queryCount');
const statusIndicator = document.getElementById('statusIndicator');
const loadingOverlay = document.getElementById('loadingOverlay');
const clearBtn = document.getElementById('clearBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadStats();
    checkHealth();
});

// Event Listeners
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Query button
    queryButton.addEventListener('click', handleQuery);
    
    // Query input - Enter to search (Ctrl+Enter for newline)
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuery();
        }
    });
    
    // Example queries
    document.querySelectorAll('.example-query').forEach(btn => {
        btn.addEventListener('click', () => {
            queryInput.value = btn.dataset.query;
            handleQuery();
        });
    });
    
    // Clear documents button
    clearBtn.addEventListener('click', handleClearDocuments);
}

// Health Check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('Ready', 'success');
        } else {
            updateStatus('Unhealthy', 'error');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('Offline', 'error');
    }
}

// Update Status Indicator
function updateStatus(text, type) {
    const statusText = statusIndicator.querySelector('.status-text');
    const statusDot = statusIndicator.querySelector('.status-dot');
    
    statusText.textContent = text;
    
    statusDot.style.background = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b'
    }[type] || '#6b7280';
}

// Load Stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        animateCounter(documentCount, data.document_count || 0);
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Animate Counter
function animateCounter(element, target) {
    const current = parseInt(element.textContent) || 0;
    const increment = Math.ceil((target - current) / 20);
    
    if (current < target) {
        element.textContent = current + increment;
        setTimeout(() => animateCounter(element, target), 20);
    } else {
        element.textContent = target;
    }
}

// File Upload Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
        showUploadStatus(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`, 'error');
        return;
    }
    
    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showUploadStatus('File too large. Maximum size is 50MB.', 'error');
        return;
    }
    
    showLoading(true);
    updateStatus('Uploading...', 'warning');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showUploadStatus(
                `✓ ${data.filename} processed successfully! Created ${data.chunks_created} chunks.`,
                'success'
            );
            loadStats(); // Refresh stats
            updateStatus('Ready', 'success');
        } else {
            showUploadStatus(`✗ Upload failed: ${data.detail}`, 'error');
            updateStatus('Ready', 'success');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showUploadStatus('✗ Upload failed. Please try again.', 'error');
        updateStatus('Ready', 'success');
    } finally {
        showLoading(false);
        fileInput.value = ''; // Reset file input
    }
}

function showUploadStatus(message, type) {
    uploadStatus.innerHTML = `<div class="status-message ${type}">${message}</div>`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        uploadStatus.innerHTML = '';
    }, 5000);
}

// Query Handler
async function handleQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        return;
    }
    
    showLoading(true);
    updateStatus('Searching...', 'warning');
    queryButton.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 5,
                include_sources: true
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data, query);
            queryCount++;
            queryCountElement.textContent = queryCount;
            updateStatus('Ready', 'success');
        } else {
            showError(`Query failed: ${data.detail}`);
            updateStatus('Ready', 'success');
        }
    } catch (error) {
        console.error('Query error:', error);
        showError('Query failed. Please try again.');
        updateStatus('Ready', 'success');
    } finally {
        showLoading(false);
        queryButton.disabled = false;
    }
}

// Display Results
function displayResults(data, query) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Build confidence badge color
    const confidenceColors = {
        'high': 'confidence-high',
        'medium': 'confidence-medium',
        'low': 'confidence-low',
        'none': 'confidence-low'
    };
    
    // Build results HTML
    let html = `
        <div class="result-answer">
            <h3>Answer</h3>
            <p>${escapeHtml(data.answer)}</p>
            <div class="result-meta">
                <span class="meta-badge ${confidenceColors[data.confidence]}">
                    Confidence: ${data.confidence.toUpperCase()}
                </span>
                <span class="meta-badge">
                    ${data.documents_searched} documents searched
                </span>
                ${data.relevant_documents ? 
                    `<span class="meta-badge">${data.relevant_documents} relevant</span>` : ''
                }
            </div>
        </div>
    `;
    
    // Add sources if available
    if (data.sources && data.sources.length > 0) {
        html += `
            <div class="result-sources">
                <h4>Sources</h4>
                ${data.sources.map(source => `
                    <div class="source-item">
                        <div class="source-header">
                            <svg class="source-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <span class="source-file">${escapeHtml(source.file)}</span>
                            <span class="source-page">• Page ${escapeHtml(source.page)}</span>
                        </div>
                        <div class="source-snippet">${escapeHtml(source.snippet)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    resultsContent.innerHTML = html;
}

// Show Error
function showError(message) {
    resultsSection.style.display = 'block';
    resultsContent.innerHTML = `
        <div class="status-message error">
            ${escapeHtml(message)}
        </div>
    `;
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Clear Documents
async function handleClearDocuments() {
    if (!confirm('Are you sure you want to clear all documents? This action cannot be undone.')) {
        return;
    }
    
    showLoading(true);
    updateStatus('Clearing...', 'warning');
    
    try {
        const response = await fetch(`${API_BASE}/documents`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showUploadStatus('✓ All documents cleared successfully!', 'success');
            loadStats(); // Refresh stats
            resultsSection.style.display = 'none';
            updateStatus('Ready', 'success');
        } else {
            showUploadStatus('✗ Failed to clear documents.', 'error');
            updateStatus('Ready', 'success');
        }
    } catch (error) {
        console.error('Clear error:', error);
        showUploadStatus('✗ Failed to clear documents.', 'error');
        updateStatus('Ready', 'success');
    } finally {
        showLoading(false);
    }
}

// Show/Hide Loading Overlay
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
