import React, { useState, useRef, useEffect, useCallback } from 'react';
import { chatAPI } from '../services/api';
import { FiSend, FiMessageSquare, FiUser, FiCpu, FiHelpCircle, FiDownload } from 'react-icons/fi';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: Date;
}

interface AIChatProps {
    configurationId: number;
    configName?: string;
}

const markdownComponents: Components = {
    p: ({ children }) => (
        <p className="m-0 text-sm leading-relaxed whitespace-pre-wrap break-words">{children}</p>
    ),
    ul: ({ children }) => (
        <ul className="my-2 pl-5 list-disc space-y-1">{children}</ul>
    ),
    ol: ({ children }) => (
        <ol className="my-2 pl-5 list-decimal space-y-1">{children}</ol>
    ),
    li: ({ children }) => (
        <li className="text-sm leading-relaxed break-words">{children}</li>
    ),
    strong: ({ children }) => (
        <strong className="font-semibold text-white">{children}</strong>
    ),
    em: ({ children }) => (
        <em className="italic">{children}</em>
    ),
    a: ({ href, children }) => (
        <a
            href={href}
            target="_blank"
            rel="noreferrer noopener"
            className="text-primary underline hover:text-primary-light break-words"
        >
            {children}
        </a>
    ),
    pre: ({ children }) => (
        <pre className="my-2 p-3 overflow-x-auto bg-black/30 border border-gray-800 text-xs">
            {children}
        </pre>
    ),
    code: (props: any) => {
        const { inline, className, children, ...rest } = props;

        if (inline) {
            return (
                <code
                    className="px-1 py-0.5 rounded bg-black/30 border border-gray-800 text-xs font-mono"
                    {...rest}
                >
                    {children}
                </code>
            );
        }

        return (
            <code className={className} {...rest}>
                {children}
            </code>
        );
    },
};

const AIChat: React.FC<AIChatProps> = ({ configurationId, configName }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Ключ для localStorage
    const storageKey = `ai_chat_session_${configurationId}`;

    const exportChatToMarkdown = () => {
        const exportDate = new Date();
        const pad2 = (n: number) => String(n).padStart(2, '0');
        const stamp = `${exportDate.getFullYear()}-${pad2(exportDate.getMonth() + 1)}-${pad2(exportDate.getDate())}_${pad2(exportDate.getHours())}-${pad2(exportDate.getMinutes())}`;

        const safeName = (configName || `config-${configurationId}`)
            .replace(/[<>:"/\\|?*]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .slice(0, 80) || `config-${configurationId}`;

        const filename = `ai-consultant_${safeName}_${stamp}.md`;
        const headerTitle = configName ? `AI Консультант — ${configName}` : 'AI Консультант';

        const md: string[] = [
            `# ${headerTitle}`,
            '',
            `Экспорт: ${exportDate.toLocaleString('ru-RU')}`,
            sessionId ? `Session: ${sessionId}` : '',
            '',
            '---',
            '',
        ].filter(Boolean);

        for (const msg of messages) {
            const roleTitle = msg.role === 'user' ? 'Пользователь' : 'AI';
            md.push(`## ${roleTitle}`);
            if (msg.timestamp) md.push(`*${msg.timestamp.toLocaleString('ru-RU')}*`, '');
            md.push((msg.content || '').trimEnd(), '', '---', '');
        }

        const blob = new Blob([md.join('\n')], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Загрузка истории чата
    const loadHistory = useCallback(async (sid: string) => {
        try {
            const response = await chatAPI.getHistory(sid);
            if (response.data.history && response.data.history.length > 0) {
                setMessages(response.data.history.map(msg => ({
                    role: msg.role,
                    content: msg.content,
                    timestamp: new Date(msg.created_at)
                })));
            } else {
                // История пустая, показываем приветствие
                setMessages([{
                    role: 'assistant',
                    content: `Привет! Я AI-консультант по вашей сборке${configName ? ` "${configName}"` : ''}. Задавайте любые вопросы о компонентах, совместимости, производительности или возможных улучшениях.`,
                    timestamp: new Date()
                }]);
            }
        } catch (err) {
            console.error('Failed to load history:', err);
            // При ошибке загрузки показываем приветствие
            setMessages([{
                role: 'assistant',
                content: `Привет! Я AI-консультант по вашей сборке${configName ? ` "${configName}"` : ''}. Задавайте любые вопросы о компонентах, совместимости, производительности или возможных улучшениях.`,
                timestamp: new Date()
            }]);
        }
    }, [configName]);

    // Загрузка сессии и истории при монтировании
    useEffect(() => {
        const savedSessionId = localStorage.getItem(storageKey);

        if (savedSessionId) {
            setSessionId(savedSessionId);
            // Загружаем историю
            loadHistory(savedSessionId);
        } else {
            // Показываем приветственное сообщение
            setMessages([{
                role: 'assistant',
                content: `Привет! Я AI-консультант по вашей сборке${configName ? ` "${configName}"` : ''}. Задавайте любые вопросы о компонентах, совместимости, производительности или возможных улучшениях.`,
                timestamp: new Date()
            }]);
        }
    }, [storageKey, loadHistory, configName]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setError(null);

        // Добавляем сообщение пользователя
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage,
            timestamp: new Date()
        }]);

        setLoading(true);

        try {
            const response = await chatAPI.sendMessage({
                message: userMessage,
                session_id: sessionId || undefined,
                configuration_id: configurationId
            });

            if (response.data.session_id) {
                setSessionId(response.data.session_id);
                // Сохраняем session_id в localStorage
                localStorage.setItem(storageKey, response.data.session_id);
            }

            // Добавляем ответ AI
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.data.response,
                timestamp: new Date()
            }]);
        } catch (err: any) {
            console.error('Chat error:', err);
            setError(err.response?.data?.error || 'Ошибка отправки сообщения. AI сервер недоступен.');

            // Добавляем сообщение об ошибке
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'К сожалению, не удалось получить ответ. Пожалуйста, попробуйте позже.',
                timestamp: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // Очистить чат и начать новую сессию
    const clearChat = () => {
        localStorage.removeItem(storageKey);
        setSessionId(null);
        setMessages([{
            role: 'assistant',
            content: `Привет! Я AI-консультант по вашей сборке${configName ? ` "${configName}"` : ''}. Задавайте любые вопросы о компонентах, совместимости, производительности или возможных улучшениях.`,
            timestamp: new Date()
        }]);
    };

    const quickQuestions = [
        'Почему выбрана эта видеокарта?',
        'Можно ли улучшить эту сборку?',
        'Какой FPS будет в играх?',
        'Есть ли проблемы совместимости?'
    ];

    return (
        <div className="card p-0 overflow-hidden flex flex-col min-h-[520px] h-[70vh] max-h-[740px]">
            {/* Header */}
            <div className="px-5 py-4 border-b border-border-dark bg-bg-card flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 flex items-center justify-center bg-primary/10 rounded-lg">
                        {React.createElement(FiMessageSquare as any, { className: "text-xl text-primary" })}
                    </div>
                    <div>
                        <h3 className="text-lg font-heading font-semibold text-white">AI Консультант</h3>
                        <p className="text-xs text-gray-500">Задавайте вопросы о сборке</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={exportChatToMarkdown}
                        className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-lg transition-colors flex items-center gap-2"
                        title="Экспортировать чат в .md"
                    >
                        {React.createElement(FiDownload as any, { className: "w-4 h-4" })}
                        Экспорт .md
                    </button>
                    {messages.length > 1 && (
                    <button
                        onClick={clearChat}
                        className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-lg transition-colors"
                    >
                        Новый чат
                    </button>
                )}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4" style={{ scrollBehavior: 'smooth' }}>
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg ${msg.role === 'user' ? 'bg-primary/20' : 'bg-green-500/20'
                            }`}>
                            {msg.role === 'user'
                                ? React.createElement(FiUser as any, { className: "text-primary" })
                                : React.createElement(FiCpu as any, { className: "text-green-400" })
                            }
                        </div>
                        <div className={`max-w-[75%] px-4 py-3 rounded-xl ${msg.role === 'user'
                            ? 'bg-primary/20 text-white'
                            : 'bg-bg-card-hover text-gray-300'
                            }`}>
                            {msg.role === 'assistant' ? (
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkBreaks]}
                                    components={markdownComponents}
                                >
                                    {msg.content}
                                </ReactMarkdown>
                            ) : (
                                <p className="text-sm leading-relaxed whitespace-pre-wrap break-words m-0">{msg.content}</p>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg bg-green-500/20">
                            {React.createElement(FiCpu as any, { className: "text-green-400 animate-pulse" })}
                        </div>
                        <div className="bg-bg-card-hover px-4 py-3 rounded-xl">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length <= 1 && (
                <div className="px-5 py-3 border-t border-border-dark bg-bg-card/50">
                    <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                        {React.createElement(FiHelpCircle as any, { className: "text-xs" })}
                        Быстрые вопросы:
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {quickQuestions.map((q, idx) => (
                            <button
                                key={idx}
                                onClick={() => setInput(q)}
                                className="text-xs px-3 py-1.5 bg-bg-card hover:bg-bg-card-hover text-gray-400 hover:text-white rounded-full transition-colors"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="px-5 py-2 bg-red-500/10 border-t border-red-500/30">
                    <p className="text-sm text-red-400">{error}</p>
                </div>
            )}

            {/* Input */}
            <div className="px-5 py-4 border-t border-border-dark bg-bg-card">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Напишите вопрос..."
                        disabled={loading}
                        style={{
                            backgroundColor: '#1a1a1a',
                            color: '#ffffff',
                            caretColor: '#10b981'
                        }}
                        className="flex-1 border border-gray-700 rounded-lg px-4 py-3 placeholder-gray-500 focus:outline-none focus:border-primary transition-colors"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className={`px-5 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${loading || !input.trim()
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            : 'bg-primary text-black hover:bg-primary-light'
                            }`}
                    >
                        {React.createElement(FiSend as any, {})}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AIChat;
