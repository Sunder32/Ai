
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5050/api'
    : (window.location.port 
        ? `${window.location.protocol}//${window.location.hostname}:${window.location.port}/api`
        : `${window.location.protocol}//${window.location.hostname}/api`);

console.log('[DEBUG] API_URL:', API_URL);


let chats = [];
let activeChat = null;
let uploadedFiles = [];


document.addEventListener('DOMContentLoaded', () => {
    loadChatsFromStorage();
    loadFilesFromStorage();
    updateChatList();
    updateFileDisplay();
    checkStatus();


    if (chats.length === 0) {
        createNewChat();
    } else {
        switchChat(chats[0].id);
    }
});


function createNewChat() {
    const newChat = {
        id: Date.now().toString(),
        title: `Chat ${chats.length + 1}`,
        messages: [{
            role: 'system',
            content: 'Welcome. I am DeepSeek. How can I assist you today?'
        }],
        context: [],
        createdAt: new Date().toISOString()
    };

    chats.unshift(newChat);
    saveChatsToStorage();
    updateChatList();
    switchChat(newChat.id);
}

function switchChat(chatId) {
    activeChat = chats.find(c => c.id === chatId);
    if (!activeChat) return;


    updateChatList();
    renderChatMessages();


    const chatContainer = document.getElementById('chat-container');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

function deleteChat(chatId, event) {
    event.stopPropagation();

    if (chats.length === 1) {
        alert('Cannot delete the last chat');
        return;
    }

    const index = chats.findIndex(c => c.id === chatId);
    if (index === -1) return;

    chats.splice(index, 1);
    saveChatsToStorage();

 
    if (activeChat && activeChat.id === chatId) {
        switchChat(chats[0].id);
    }

    updateChatList();
}

function updateChatList() {
    const chatListEl = document.getElementById('chat-list');
    chatListEl.innerHTML = '';

    chats.forEach(chat => {
        const lastMessage = chat.messages[chat.messages.length - 1];
        const preview = lastMessage ? lastMessage.content.substring(0, 50) : 'No messages';

        const chatItem = document.createElement('div');
        chatItem.className = `chat-item ${activeChat && activeChat.id === chat.id ? 'active' : ''}`;
        chatItem.onclick = () => switchChat(chat.id);

        chatItem.innerHTML = `
            <div class="chat-item-content">
                <div class="chat-item-title">${chat.title}</div>
                <div class="chat-item-preview">${preview}...</div>
            </div>
            <button class="chat-delete-btn" onclick="deleteChat('${chat.id}', event)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        chatListEl.appendChild(chatItem);
    });
}

function renderChatMessages() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = '';

    if (!activeChat) return;

    activeChat.messages.forEach(msg => {
        appendMessage(msg.content, msg.role, false, false);
    });
}


function saveChatsToStorage() {
    try {
        localStorage.setItem('deepseek_chats', JSON.stringify(chats));
    } catch (e) {
        console.error('Failed to save chats:', e);
    }
}

function loadChatsFromStorage() {
    try {
        const stored = localStorage.getItem('deepseek_chats');
        if (stored) {
            chats = JSON.parse(stored);
        }
    } catch (e) {
        console.error('Failed to load chats:', e);
        chats = [];
    }
}

function saveFilesToStorage() {
    try {
        localStorage.setItem('deepseek_files', JSON.stringify(uploadedFiles));
    } catch (e) {
        console.error('Failed to save files:', e);
    }
}

function loadFilesFromStorage() {
    try {
        const stored = localStorage.getItem('deepseek_files');
        if (stored) {
            uploadedFiles = JSON.parse(stored);
        }
    } catch (e) {
        console.error('Failed to load files:', e);
        uploadedFiles = [];
    }
}


function switchTab(tabName) {
    document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));

    document.getElementById(`${tabName}-view`).classList.add('active');
    const buttons = document.querySelectorAll('.nav-btn');
    if (tabName === 'chat') buttons[0].classList.add('active');
    if (tabName === 'rag') buttons[1].classList.add('active');
    if (tabName === 'train') buttons[2].classList.add('active');
    if (tabName === 'finetune') buttons[3].classList.add('active');
    if (tabName === 'learning') buttons[4].classList.add('active');
    

    if (tabName === 'rag') loadRAGStats();
    if (tabName === 'finetune') loadFinetuneInfo();
    if (tabName === 'learning') loadLearningStats();
}


const userInput = document.getElementById('user-input');

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    if (!activeChat) return;

    const text = userInput.value.trim();
    if (!text) return;


    activeChat.messages.push({ role: 'user', content: text });
    appendMessage(text, 'user', true);
    userInput.value = '';


    const loadingId = appendMessage('Thinking...', 'system', true, true);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: text,
                context: activeChat.context || []
            })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();


        removeMessage(loadingId);


        activeChat.messages.push({ role: 'system', content: data.response });
        appendMessage(data.response, 'system', true);

        activeChat.context = data.context;


        saveChatsToStorage();

    } catch (error) {
        removeMessage(loadingId);
        const errorMsg = `Error: ${error.message}. Make sure the backend is running!`;
        activeChat.messages.push({ role: 'system', content: errorMsg });
        appendMessage(errorMsg, 'system', true);
    }
}

function appendMessage(text, sender, shouldSave = false, isLoading = false) {
    const chatContainer = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    const msgId = `msg-${Date.now()}`;
    if (isLoading) msgDiv.id = msgId;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    

    if (sender === 'system' && !isLoading) {
        bubble.innerHTML = renderMarkdown(text);
    } else {
        bubble.textContent = text;
    }

    msgDiv.appendChild(bubble);
    

    if (sender === 'system' && !isLoading) {
        const actions = document.createElement('div');
        actions.className = 'message-actions';
        actions.innerHTML = `
            <button class="action-btn like-btn" onclick="likeMessage(this)" title="Хороший ответ">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                </svg>
            </button>
            <button class="action-btn edit-btn" onclick="editMessage(this)" title="Исправить ответ">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
            </button>
            <button class="action-btn copy-btn" onclick="copyMessage(this)" title="Копировать">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
            </button>
            <button class="action-btn download-btn" onclick="downloadMessage(this)" title="Скачать как файл">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
            </button>
        `;
        msgDiv.appendChild(actions);
        

        msgDiv.dataset.originalText = text;
        msgDiv.dataset.prompt = activeChat?.messages[activeChat.messages.length - 2]?.content || '';
    }
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (shouldSave) {
        saveChatsToStorage();
        updateChatList();
    }

    return msgId;
}


function renderMarkdown(text) {

    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    

    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre class="code-block" data-lang="${lang || 'text'}"><code>${code.trim()}</code></pre>`;
    });
    

    html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');


    html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');
    

    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    

    html = html.replace(/^\- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    

    html = html.replace(/\n/g, '<br>');
    
    return html;
}


async function likeMessage(btn) {
    const msgDiv = btn.closest('.message');
    const text = msgDiv.dataset.originalText;
    const prompt = msgDiv.dataset.prompt;
    
    try {
        const res = await fetch(`${API_URL}/learning/like`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, response: text })
        });
        
        if (res.ok) {
            btn.classList.add('liked');
            btn.innerHTML = '👍';
            showToast('Спасибо! ИИ будет учиться на этом примере.');
        }
    } catch (e) {
        console.error('Like error:', e);
    }
}


function editMessage(btn) {
    const msgDiv = btn.closest('.message');
    const bubble = msgDiv.querySelector('.bubble');
    const originalText = msgDiv.dataset.originalText;
    const prompt = msgDiv.dataset.prompt;
    

    const editor = document.createElement('div');
    editor.className = 'message-editor';
    editor.innerHTML = `
        <textarea class="edit-textarea">${originalText}</textarea>
        <input type="text" class="edit-feedback" placeholder="Что было не так? (опционально)">
        <div class="edit-actions">
            <button class="edit-save" onclick="saveEdit(this)">💾 Сохранить исправление</button>
            <button class="edit-cancel" onclick="cancelEdit(this)">❌ Отмена</button>
        </div>
    `;
    
    editor.dataset.originalText = originalText;
    editor.dataset.prompt = prompt;
    
    bubble.style.display = 'none';
    msgDiv.querySelector('.message-actions').style.display = 'none';
    msgDiv.appendChild(editor);
}


async function saveEdit(btn) {
    const editor = btn.closest('.message-editor');
    const msgDiv = editor.closest('.message');
    const bubble = msgDiv.querySelector('.bubble');
    
    const originalText = editor.dataset.originalText;
    const prompt = editor.dataset.prompt;
    const correctedText = editor.querySelector('.edit-textarea').value;
    const feedback = editor.querySelector('.edit-feedback').value;
    
    try {
        const res = await fetch(`${API_URL}/learning/correct`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                original_response: originalText,
                corrected_response: correctedText,
                feedback
            })
        });
        
        if (res.ok) {

            bubble.innerHTML = renderMarkdown(correctedText);
            msgDiv.dataset.originalText = correctedText;
            

            editor.remove();
            bubble.style.display = 'block';
            msgDiv.querySelector('.message-actions').style.display = 'flex';
            
            showToast('✅ Исправление сохранено! ИИ учтёт это в будущем.');
            

            if (activeChat) {
                const lastMsgIndex = activeChat.messages.length - 1;
                if (activeChat.messages[lastMsgIndex]) {
                    activeChat.messages[lastMsgIndex].content = correctedText;
                    saveChatsToStorage();
                }
            }
        }
    } catch (e) {
        console.error('Save edit error:', e);
        showToast('❌ Ошибка сохранения');
    }
}


function cancelEdit(btn) {
    const editor = btn.closest('.message-editor');
    const msgDiv = editor.closest('.message');
    const bubble = msgDiv.querySelector('.bubble');
    
    editor.remove();
    bubble.style.display = 'block';
    msgDiv.querySelector('.message-actions').style.display = 'flex';
}


function copyMessage(btn) {
    const msgDiv = btn.closest('.message');
    const text = msgDiv.dataset.originalText;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('📋 Скопировано!');
    });
}


function downloadMessage(btn) {
    const msgDiv = btn.closest('.message');
    const text = msgDiv.dataset.originalText;
    

    let ext = 'md';
    if (text.includes('```python')) ext = 'py';
    else if (text.includes('```javascript')) ext = 'js';
    else if (text.includes('```html')) ext = 'html';
    else if (text.includes('```css')) ext = 'css';
    else if (text.includes('```json')) ext = 'json';
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `response_${Date.now()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('📥 Файл скачан!');
}


function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}


const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-upload');

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFiles);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#3b82f6';
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    const files = e.dataTransfer.files;
    handleFiles({ target: { files } });
});

async function handleFiles(e) {
    const files = e.target.files;
    if (!files.length) return;

    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/train/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                uploadedFiles.push({
                    name: file.name,
                    size: file.size,
                    uploadedAt: new Date().toISOString()
                });
                saveFilesToStorage();
                updateFileDisplay();
            } else {
                alert(`Upload failed: ${result.message || 'Unknown error'}`);
            }

        } catch (error) {
            alert('Upload failed: ' + error.message);
        }
    }


    fileInput.value = '';
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    saveFilesToStorage();
    updateFileDisplay();
}

function updateFileDisplay() {
    const fileListEl = document.getElementById('file-list');
    const fileCountEl = document.getElementById('file-count');
    const trainBtn = document.getElementById('train-btn');

    fileCountEl.textContent = uploadedFiles.length;


    trainBtn.disabled = uploadedFiles.length === 0;

    fileListEl.innerHTML = '';

    uploadedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        fileItem.innerHTML = `
            <div class="file-info">
                <svg class="file-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <span class="file-name">${file.name}</span>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        fileListEl.appendChild(fileItem);
    });
}


async function startTraining() {
    if (uploadedFiles.length === 0) {
        alert('Please upload files first');
        return;
    }

    const trainBtn = document.getElementById('train-btn');
    const progressEl = document.getElementById('training-progress');
    const statusEl = document.getElementById('training-status');
    const progressFill = document.getElementById('progress-fill');

    trainBtn.disabled = true;
    progressEl.style.display = 'block';
    statusEl.textContent = 'Starting training...';
    progressFill.style.width = '10%';

    try {
        statusEl.textContent = 'Processing files...';
        progressFill.style.width = '30%';

        const response = await fetch(`${API_URL}/train/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        progressFill.style.width = '60%';

        if (!response.ok) {
            throw new Error(' Training failed');
        }

        const result = await response.json();

        statusEl.textContent = 'Training complete!';
        progressFill.style.width = '100%';

        setTimeout(() => {
            alert('Model training completed successfully!');
            progressEl.style.display = 'none';
            trainBtn.disabled = false;
            progressFill.style.width = '0%';
        }, 2000);

    } catch (error) {
        statusEl.textContent = 'Training failed: ' + error.message;
        progressFill.style.width = '0%';
        alert('Training failed: ' + error.message);

        setTimeout(() => {
            progressEl.style.display = 'none';
            trainBtn.disabled = false;
        }, 3000);
    }
}

async function checkStatus() {
    try {
        const res = await fetch(`${API_URL}/models`);
        if (res.ok) {
            document.getElementById('model-status').textContent = 'Online';
            document.querySelector('.indicator').style.backgroundColor = '#22c55e';
            document.querySelector('.indicator').style.boxShadow = '0 0 10px #22c55e';
        } else {
            throw new Error('Backend unreachable');
        }
    } catch (e) {
        console.error('[ERROR] Не удалось подключиться к API:', e);
        console.error('[DEBUG] Попытка подключения к:', API_URL);
        console.error('[DEBUG] Текущий протокол:', window.location.protocol);
        console.error('[DEBUG] Текущий хост:', window.location.hostname);
        
        document.getElementById('model-status').textContent = 'Offline';
        document.querySelector('.indicator').style.backgroundColor = '#ef4444';
        document.querySelector('.indicator').style.boxShadow = '0 0 10px #ef4444';
        

        if (window.location.protocol === 'https:' && API_URL.startsWith('http:')) {
            console.warn('[ВНИМАНИЕ] Mixed Content! HTTPS страница пытается подключиться к HTTP API.');
            console.warn('[РЕШЕНИЕ] Используйте Cloudflare Tunnel или локальную сеть.');
        }
    }
}




async function loadRAGStats() {
    try {
        const res = await fetch(`${API_URL}/rag/stats`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('rag-chunks').textContent = data.total_chunks || 0;
        }
    } catch (e) {
        console.error('Failed to load RAG stats:', e);
    }
}

async function indexRAG() {
    try {
        const btn = event.target.closest('button');
        btn.disabled = true;
        btn.innerHTML = '⏳ Индексация...';
        
        const res = await fetch(`${API_URL}/rag/index`, { method: 'POST' });
        const data = await res.json();
        
        if (res.ok) {
            alert(`✅ Индексация завершена!\nФайлов: ${data.files_processed}\nЧанков: ${data.chunks_created}`);
            loadRAGStats();
        } else {
            alert('❌ Ошибка: ' + (data.detail || 'Unknown error'));
        }
    } catch (e) {
        alert('❌ Ошибка: ' + e.message);
    } finally {
        const btn = event.target.closest('button');
        btn.disabled = false;
        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg> Индексировать документы`;
    }
}

const ragInput = document.getElementById('rag-input');
if (ragInput) {
    ragInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendRAGMessage();
    });
}

async function sendRAGMessage() {
    const input = document.getElementById('rag-input');
    const text = input.value.trim();
    if (!text) return;
    
    const container = document.getElementById('rag-chat-container');
    

    container.innerHTML += `<div class="message user"><div class="bubble">${text}</div></div>`;
    input.value = '';
    

    const loadingId = 'rag-loading-' + Date.now();
    container.innerHTML += `<div class="message system" id="${loadingId}"><div class="bubble">🔍 Поиск в документах...</div></div>`;
    container.scrollTop = container.scrollHeight;
    
    try {
        const res = await fetch(`${API_URL}/chat/rag`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text, context: [] })
        });
        
        const data = await res.json();
        

        document.getElementById(loadingId)?.remove();
        

        const ragBadge = data.rag_context_used ? '<span class="rag-badge">📚 RAG</span>' : '';
        container.innerHTML += `<div class="message system"><div class="bubble">${ragBadge}${data.response}</div></div>`;
        container.scrollTop = container.scrollHeight;
        
    } catch (e) {
        document.getElementById(loadingId)?.remove();
        container.innerHTML += `<div class="message system"><div class="bubble">❌ Ошибка: ${e.message}</div></div>`;
    }
}




function addLog(message, type = 'info') {
    const logContent = document.getElementById('log-content');
    const time = new Date().toLocaleTimeString();
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    logContent.innerHTML += `<p class="log-${type}">[${time}] ${icon} ${message}</p>`;
    logContent.scrollTop = logContent.scrollHeight;
}

async function loadFinetuneInfo() {
    try {
        const res = await fetch(`${API_URL}/finetune/info`);
        const data = await res.json();
        
        const infoDiv = document.getElementById('finetune-info');
        
        if (data.datasets && data.datasets.length > 0) {
            let html = '<h3>📊 Найденные датасеты:</h3>';
            for (const ds of data.datasets) {
                html += `
                    <div class="dataset-card">
                        <strong>${ds.filename}</strong>
                        <p>Записей: ${ds.total_samples || 'N/A'}</p>
                        <p>Поля: ${(ds.fields || []).join(', ')}</p>
                        ${ds.labels_distribution ? `<p>Классы: ${JSON.stringify(ds.labels_distribution)}</p>` : ''}
                    </div>
                `;
            }
            infoDiv.innerHTML = html;
            addLog(`Найдено ${data.datasets.length} датасет(ов)`, 'success');
        } else {
            infoDiv.innerHTML = '<p class="no-data">Нет JSON датасетов. Загрузите файлы во вкладке Knowledge.</p>';
            addLog('Датасеты не найдены', 'error');
        }
    } catch (e) {
        addLog('Ошибка загрузки информации: ' + e.message, 'error');
    }
}

async function prepareFinetuneData() {
    try {
        addLog('Подготовка данных для fine-tuning...', 'info');
        
        const res = await fetch(`${API_URL}/finetune/prepare`, { method: 'POST' });
        const data = await res.json();
        
        if (res.ok) {
            addLog(`Подготовлено файлов: ${data.files.length}`, 'success');
            for (const f of data.files) {
                addLog(`→ ${f.source} → ${f.output}`, 'info');
            }
        } else {
            addLog('Ошибка: ' + (data.detail || 'Unknown'), 'error');
        }
    } catch (e) {
        addLog('Ошибка: ' + e.message, 'error');
    }
}

async function createFinetunedModel() {
    try {
        addLog('Создание модели с few-shot примерами...', 'info');
        
        const res = await fetch(`${API_URL}/finetune/create-model`, { method: 'POST' });
        const data = await res.json();
        
        if (res.ok) {
            addLog(`Модель "${data.model_name}" успешно создана! 🎉`, 'success');
            alert(`✅ Модель ${data.model_name} создана!\n\nИспользуйте в терминале:\nollama run ${data.model_name}`);
        } else {
            addLog('Ошибка: ' + (data.detail || 'Unknown'), 'error');
        }
    } catch (e) {
        addLog('Ошибка: ' + e.message, 'error');
    }
}




async function loadLearningStats() {
    try {
        const res = await fetch(`${API_URL}/learning/stats`);
        const data = await res.json();
        
        document.getElementById('corrections-count').textContent = data.corrections_count || 0;
        document.getElementById('good-responses-count').textContent = data.good_responses_count || 0;
        document.getElementById('total-learning').textContent = data.total_examples || 0;
        
        showToast('📊 Статистика обновлена');
    } catch (e) {
        console.error('Load learning stats error:', e);
        showToast('❌ Ошибка загрузки статистики');
    }
}

async function exportLearningData() {
    try {
        const res = await fetch(`${API_URL}/learning/export`, { method: 'GET' });
        const data = await res.json();
        
        console.log('Export data:', data);
        
        if (data.examples && data.examples.length > 0) {

            const jsonl = data.examples.map(ex => JSON.stringify(ex)).join('\n');
            const blob = new Blob([jsonl], { type: 'application/jsonl' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `learning_data_${Date.now()}.jsonl`;
            a.click();
            URL.revokeObjectURL(url);
            
            showToast(`📥 Экспортировано ${data.examples.length} примеров`);
        } else {
            showToast('⚠️ Нет данных для экспорта');
        }
    } catch (e) {
        console.error('Export learning data error:', e);
        showToast('❌ Ошибка экспорта');
    }
}
