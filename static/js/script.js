// API Base URL
const API_BASE = window.location.origin;

// Load dashboard statistics on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
});

// Helper function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    return response.json();
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const stats = await apiCall('/api/dashboard-stats');
        
        document.getElementById('totalTransactions').textContent = stats.total_transactions.toLocaleString();
        document.getElementById('totalCustomers').textContent = stats.total_customers.toLocaleString();
        document.getElementById('totalMerchants').textContent = stats.total_merchants.toLocaleString();
        document.getElementById('avgTransaction').textContent = '$' + stats.avg_transaction.toFixed(2);
        
        // Populate category dropdowns
        const categorySelect = document.getElementById('category');
        const transactionCategorySelect = document.getElementById('transactionCategory');
        
        categorySelect.innerHTML = '<option value="">Choose a category</option>';
        transactionCategorySelect.innerHTML = '';
        
        stats.categories.forEach(cat => {
            categorySelect.innerHTML += `<option value="${cat}">${cat}</option>`;
            transactionCategorySelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        });
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Merchant Trust Score
async function getMerchantTrustScore() {
    const merchantName = document.getElementById('merchantName').value.trim();
    const resultDiv = document.getElementById('trustScoreResult');
    const btn = document.getElementById('merchantBtn');

    if (!merchantName) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a merchant name</div>';
        resultDiv.classList.add('show');
        return;
    }

    // Show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/merchant-trust', 'POST', { merchant_name: merchantName });
        
        resultDiv.innerHTML = `
            <div class="result-title">Trust Score Analysis</div>
            <div class="result-value">${result.merchant_name}</div>
            <div class="trust-score">
                <span>Trust Score:</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${result.trust_score}%">${result.trust_score}/100</div>
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Total Transactions</div>
                    <div class="stat-box-value">${result.total_transactions}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Avg Amount</div>
                    <div class="stat-box-value">$${result.avg_amount.toFixed(2)}</div>
                </div>
            </div>
            <div class="result-details">
                <strong>Category:</strong> ${result.category}<br>
                <strong>Rating:</strong> <span class="badge ${result.trust_score >= 85 ? 'badge-high' : result.trust_score >= 70 ? 'badge-medium' : 'badge-low'}">${result.rating}</span>
            </div>
            <div class="alert ${result.trust_score >= 80 ? 'alert-success' : result.trust_score >= 60 ? 'alert-info' : 'alert-warning'}">
                ${result.trust_score >= 80 ? '✓ Highly trusted merchant' : result.trust_score >= 60 ? 'ℹ Moderate trust level' : '⚠ Exercise caution'}
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'Merchant not found'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Get Trust Score';
    }
}

// Customer Analysis
async function getCustomerAnalysis() {
    const customerId = document.getElementById('customerId').value;
    const resultDiv = document.getElementById('customerResult');
    const btn = document.getElementById('customerBtn');

    if (!customerId) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a customer ID</div>';
        resultDiv.classList.add('show');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/customer-analysis', 'POST', { customer_id: customerId });
        
        resultDiv.innerHTML = `
            <div class="result-title">Customer Profile</div>
            <div class="result-value">${result.name}</div>
            <div class="result-details">
                <strong>ID:</strong> ${result.customer_id}<br>
                <strong>Age:</strong> ${result.age || 'N/A'} years<br>
                <strong>Gender:</strong> ${result.gender === 'M' ? 'Male' : 'Female'}
            </div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Total Spending</div>
                    <div class="stat-box-value">$${result.total_spending.toFixed(2)}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Transactions</div>
                    <div class="stat-box-value">${result.transaction_count}</div>
                </div>
            </div>
            <div class="result-details">
                <strong>Average Transaction:</strong> $${result.avg_transaction.toFixed(2)}<br>
                <strong>Spending Level:</strong> <span class="badge ${result.spending_level === 'High' ? 'badge-high' : result.spending_level === 'Medium' ? 'badge-medium' : 'badge-low'}">${result.spending_level} Spender</span><br>
                <strong>Favorite Category:</strong> ${result.favorite_category}
            </div>
            <div class="alert alert-info">
                Customer shows ${result.spending_level.toLowerCase()} spending behavior with consistent transaction patterns
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'Customer not found'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Analyze Customer';
    }
}

// Category Insights
async function getCategoryInsights() {
    const category = document.getElementById('category').value;
    const resultDiv = document.getElementById('categoryResult');
    const btn = document.getElementById('categoryBtn');

    if (!category) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please select a category</div>';
        resultDiv.classList.add('show');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/category-insights', 'POST', { category: category });
        
        const trendIcon = result.trend === 'increasing' ? '📈' : result.trend === 'decreasing' ? '📉' : '➡️';
        
        resultDiv.innerHTML = `
            <div class="result-title">${result.category} Category</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Avg Amount</div>
                    <div class="stat-box-value">$${result.avg_amount.toFixed(2)}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Total Transactions</div>
                    <div class="stat-box-value">${result.total_transactions}</div>
                </div>
            </div>
            <div class="result-details">
                <strong>Market Trend:</strong> ${trendIcon} ${result.trend.charAt(0).toUpperCase() + result.trend.slice(1)}<br>
                <strong>Popularity:</strong> ${result.popularity}<br>
                <strong>Market Share:</strong> ${result.market_share}%
            </div>
            <div class="alert alert-info">
                ${result.category} category shows ${result.trend} trend with ${result.total_transactions} total transactions
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'Category not found'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Get Insights';
    }
}

// Risk Assessment
async function assessRisk() {
    const amount = parseFloat(document.getElementById('transactionAmount').value);
    const category = document.getElementById('transactionCategory').value;
    const resultDiv = document.getElementById('riskResult');
    const btn = document.getElementById('riskBtn');

    if (!amount || !category) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter amount and select category</div>';
        resultDiv.classList.add('show');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/risk-assessment', 'POST', { amount: amount, category: category });
        
        const riskColor = result.risk_score < 40 ? '#6bcf7f' : result.risk_score < 70 ? '#ffd93d' : '#ff6b6b';
        
        resultDiv.innerHTML = `
            <div class="result-title">Risk Assessment</div>
            <div class="result-value">$${result.amount.toFixed(2)}</div>
            <div class="trust-score">
                <span>Risk Level:</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${result.risk_score}%; background: ${riskColor}">${result.risk_score}%</div>
                </div>
            </div>
            <div class="result-details">
                <strong>Category Average:</strong> $${result.category_avg.toFixed(2)}<br>
                <strong>Deviation:</strong> ${result.deviation > 0 ? '+' : ''}${result.deviation}%<br>
                <strong>Z-Score:</strong> ${result.z_score}<br>
                <strong>Risk Rating:</strong> <span class="badge ${result.risk_score < 40 ? 'badge-high' : result.risk_score < 70 ? 'badge-medium' : 'badge-low'}">${result.risk_level}</span>
            </div>
            <div class="alert ${result.risk_score < 40 ? 'alert-success' : result.risk_score < 70 ? 'alert-info' : 'alert-warning'}">
                ${result.risk_score < 40 ? '✓ Transaction amount is within normal range' : result.risk_score < 70 ? 'ℹ Transaction amount is slightly elevated' : '⚠ Transaction amount significantly deviates from category average'}
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'Unable to assess risk'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Assess Risk';
    }
}

// City Analysis
async function getCityAnalysis() {
    const cityName = document.getElementById('cityName').value.trim();
    const resultDiv = document.getElementById('cityResult');
    const btn = document.getElementById('cityBtn');

    if (!cityName) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a city name</div>';
        resultDiv.classList.add('show');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/city-analysis', 'POST', { city_name: cityName });
        
        resultDiv.innerHTML = `
            <div class="result-title">City Analytics</div>
            <div class="result-value">${result.city}</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Total Volume</div>
                    <div class="stat-box-value">$${result.total_volume.toFixed(2)}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Transactions</div>
                    <div class="stat-box-value">${result.total_transactions}</div>
                </div>
            </div>
            <div class="result-details">
                <strong>Average Transaction:</strong> $${result.avg_transaction.toFixed(2)}<br>
                <strong>Activity Level:</strong> <span class="badge ${result.activity_level === 'Very High' ? 'badge-high' : 'badge-medium'}">${result.activity_level}</span><br>
                <strong>Top Category:</strong> ${result.top_category}
            </div>
            <div class="alert alert-info">
                ${result.city} shows ${result.activity_level.toLowerCase()} transaction activity with strong spending patterns
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'City not found'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Analyze City';
    }
}

// Spending Predictor
async function predictSpending() {
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const resultDiv = document.getElementById('predictResult');
    const btn = document.getElementById('predictBtn');

    if (!age) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter age</div>';
        resultDiv.classList.add('show');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Loading...';
    resultDiv.classList.remove('show');

    try {
        const result = await apiCall('/api/spending-prediction', 'POST', { age: age, gender: gender });
        
        resultDiv.innerHTML = `
            <div class="result-title">Spending Prediction</div>
            <div class="result-value">$${result.predicted_monthly_spending.toFixed(2)}/month</div>
            <div class="result-details">
                <strong>Age Group:</strong> ${result.age_group}<br>
                <strong>Gender:</strong> ${result.gender}<br>
                <strong>Confidence:</strong> ${result.confidence.toFixed(1)}%
            </div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Expected Frequency</div>
                    <div class="stat-box-value">${result.predicted_frequency}/month</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Top Category</div>
                    <div class="stat-box-value">${result.top_category}</div>
                </div>
            </div>
            <div class="alert alert-success">
                ✓ Prediction based on demographic patterns and historical data
            </div>
        `;
        resultDiv.classList.add('show');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">❌ ${error.error || 'Unable to predict'}</div>`;
        resultDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Predict Spending';
    }
}