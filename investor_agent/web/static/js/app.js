/**
 * Investor Assistant - Web Application
 * AI-агент для поддержки инвестиционной деятельности
 * Свердловская область
 */

// ==================== Constants ====================
const API_BASE = '/api';

// ==================== Navigation ====================

/**
 * Переключение между вкладками
 * @param {string} sectionId - ID секции для отображения
 */
function showSection(sectionId) {
    // Скрываем все секции
    document.querySelectorAll('.content-section').forEach(s => 
        s.classList.remove('active')
    );
    
    // Деактивируем все вкладки
    document.querySelectorAll('.nav-tab').forEach(t => 
        t.classList.remove('active')
    );
    
    // Показываем нужную секцию
    document.getElementById(sectionId).classList.add('active');
    
    // Активируем соответствующую вкладку
    event.target.classList.add('active');
}

// ==================== API Utilities ====================

/**
 * Выполнение API запроса
 * @param {string} endpoint - URL endpoint
 * @param {string} method - HTTP метод
 * @param {object|null} data - Данные для отправки
 * @returns {Promise<object>} - Ответ API
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(API_BASE + endpoint, options);
    return await response.json();
}

// ==================== UI Helpers ====================

/**
 * Отображение индикатора загрузки
 * @param {string} elementId - ID элемента для отображения
 */
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Загрузка...</p>
        </div>
    `;
}

/**
 * Отображение ошибки
 * @param {string} elementId - ID элемента для отображения
 * @param {string} message - Текст ошибки
 */
function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `
        <div class="error">❌ ${message}</div>
    `;
}

// ==================== Search Functions ====================

/**
 * Поиск лучших отраслевых практик
 */
async function searchPractices() {
    const industry = document.getElementById('practice-industry').value;
    showLoading('practices-results');
    
    try {
        const result = await apiRequest('/practices', 'POST', { industry });
        
        if (result.success) {
            let html = '';
            result.data.forEach(p => {
                // Определение класса для score
                const scoreClass = p.applicability_score >= 0.7 ? 'score-high' : 
                                  p.applicability_score >= 0.4 ? 'score-medium' : 'score-low';
                
                html += `
                    <div class="result-card">
                        <h3>${p.name}</h3>
                        <div class="meta">
                            <span>📍 ${p.region}</span>
                            <span>🏭 ${p.industry}</span>
                            <span class="${scoreClass}">📊 Применимость: ${(p.applicability_score * 100).toFixed(0)}%</span>
                        </div>
                        <p>${p.description}</p>
                        <p><strong>Результаты:</strong> ${p.results}</p>
                        ${p.recommendations.length > 0 ? `
                            <p><strong>Рекомендации:</strong></p>
                            <ul class="checklist">
                                ${p.recommendations.map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `;
            });
            
            document.getElementById('practices-results').innerHTML = 
                html || '<p>Практики не найдены</p>';
        } else {
            showError('practices-results', result.error);
        }
    } catch (e) {
        showError('practices-results', e.message);
    }
}

/**
 * Поиск инвестиционных возможностей
 */
async function searchOpportunities() {
    const industry = document.getElementById('opp-industry').value;
    const minInvestment = parseFloat(document.getElementById('opp-min-investment').value);
    showLoading('opportunities-results');
    
    try {
        const result = await apiRequest('/opportunities', 'POST', { 
            industry, 
            min_investment: minInvestment 
        });
        
        if (result.success) {
            let html = '';
            result.data.forEach(o => {
                html += `
                    <div class="result-card">
                        <h3>${o.title}</h3>
                        <div class="meta">
                            <span>📍 ${o.location}</span>
                            <span>🏢 ${o.type}</span>
                            <span>💰 ${(o.investment_required / 1000000).toFixed(1)} млн ₽</span>
                        </div>
                        <p>${o.description}</p>
                        ${o.potential_return ? 
                            `<p><strong>Доходность:</strong> ${o.potential_return}</p>` : ''}
                    </div>
                `;
            });
            
            document.getElementById('opportunities-results').innerHTML = 
                html || '<p>Возможности не найдены</p>';
        } else {
            showError('opportunities-results', result.error);
        }
    } catch (e) {
        showError('opportunities-results', e.message);
    }
}

/**
 * Поиск мер государственной поддержки
 */
async function searchSupport() {
    const industry = document.getElementById('support-industry').value;
    showLoading('support-results');
    
    try {
        const result = await apiRequest('/support-measures', 'POST', { industry });
        
        if (result.success) {
            let html = '';
            result.data.forEach(m => {
                // Иконки для типов мер поддержки
                const typeIcons = {
                    'grant': '💰',
                    'subsidy': '📋',
                    'tax_benefit': '📉',
                    'guarantee': '🛡️'
                };
                
                html += `
                    <div class="result-card">
                        <h3>${typeIcons[m.type] || '📄'} ${m.name}</h3>
                        <div class="meta">
                            <span>Тип: ${m.type}</span>
                            <span>💵 до ${(m.max_amount / 1000000).toFixed(1)} млн ₽</span>
                            ${m.deadline ? `<span>📅 До: ${m.deadline}</span>` : ''}
                        </div>
                        <p>${m.description}</p>
                        <p><strong>Требования:</strong></p>
                        <ul class="checklist">
                            ${m.eligibility.map(e => `<li>${e}</li>`).join('')}
                        </ul>
                        <p><strong>Документы:</strong> ${m.documents_required.join(', ')}</p>
                        <p><strong>Контакты:</strong> ${m.contact_info}</p>
                    </div>
                `;
            });
            
            document.getElementById('support-results').innerHTML = 
                html || '<p>Меры поддержки не найдены</p>';
        } else {
            showError('support-results', result.error);
        }
    } catch (e) {
        showError('support-results', e.message);
    }
}

// ==================== Document Functions ====================

/**
 * Подготовка пакета документов
 */
async function prepareDocuments() {
    const measureType = document.getElementById('doc-type').value;
    const applicant = document.getElementById('doc-applicant').value;
    const inn = document.getElementById('doc-inn').value;
    
    // Валидация
    if (!applicant || !inn) {
        showError('documents-results', 'Заполните все поля');
        return;
    }
    
    showLoading('documents-results');
    
    try {
        // Данные проекта (в реальном приложении брать из формы)
        const projectData = {
            applicant_name: applicant,
            inn: inn,
            project_name: "Инвестиционный проект",
            investment_amount: 50000000,
            grant_amount: 15000000,
            jobs_created: 25,
            description: "Реализация инвестиционного проекта"
        };
        
        const result = await apiRequest('/documents/package', 'POST', {
            measure_name: "Грант на развитие производства",
            measure_type: measureType,
            project_data: projectData
        });
        
        if (result.success) {
            const pkg = result.data;
            let html = `
                <div class="result-card">
                    <h3>📦 Пакет документов: ${pkg.package_id}</h3>
                    <div class="meta">
                        <span>Мера: ${pkg.measure_name}</span>
                        <span>Статус: ${pkg.status}</span>
                    </div>
                    <p><strong>Документы:</strong></p>
                    <ul class="checklist">
                        ${pkg.documents.map(d => `
                            <li>${d.filename} (${d.status})</li>
                        `).join('')}
                    </ul>
                </div>
            `;
            
            document.getElementById('documents-results').innerHTML = html;
        } else {
            showError('documents-results', result.error);
        }
    } catch (e) {
        showError('documents-results', e.message);
    }
}

// ==================== Analysis Functions ====================

/**
 * Запуск комплексного анализа отрасли
 */
async function runAnalysis() {
    const industry = document.getElementById('analysis-industry').value;
    showLoading('analysis-results');
    
    try {
        const result = await apiRequest('/analysis/full', 'POST', { industry });
        
        if (result.success) {
            const data = result.data;
            let html = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>${data.sections.best_practices.length}</h3>
                        <p>Лучших практик</p>
                    </div>
                    <div class="stat-card">
                        <h3>${data.sections.opportunities.length}</h3>
                        <p>Инвестплощадок</p>
                    </div>
                    <div class="stat-card">
                        <h3>${data.sections.support_measures.length}</h3>
                        <p>Мер поддержки</p>
                    </div>
                </div>
                
                <div class="result-card">
                    <h3>📋 Рекомендации</h3>
                    <ul class="checklist">
                        ${data.sections.recommendations.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            document.getElementById('analysis-results').innerHTML = html;
        } else {
            showError('analysis-results', result.error);
        }
    } catch (e) {
        showError('analysis-results', e.message);
    }
}

// ==================== Initialization ====================

/**
 * Проверка доступности API при загрузке страницы
 */
window.addEventListener('load', async () => {
    try {
        const response = await fetch(API_BASE + '/health');
        const data = await response.json();
        console.log('✅ API Status:', data.status);
        console.log('📍 Region:', data.region);
        console.log('📅 Timestamp:', data.timestamp);
    } catch (e) {
        console.error('❌ API not available:', e.message);
    }
});

// ==================== Exports ====================
// Делаем функции доступными глобально для HTML
window.showSection = showSection;
window.searchPractices = searchPractices;
window.searchOpportunities = searchOpportunities;
window.searchSupport = searchSupport;
window.prepareDocuments = prepareDocuments;
window.runAnalysis = runAnalysis;
