import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import GlassPanel from './GlassPanel';

export default function ChatPanel() {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'سلام. من Elen-k هستم. چطور می‌تونم کمکت کنم؟' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      // ارسال پیام به API سایت
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      
      const data = await res.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { role: 'ai', text: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: 'خطا در پردازش: ' + data.error }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', text: 'ارتباط با سرور برقرار نشد.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <GlassPanel className="flex flex-col h-[400px] w-full">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-blue-500/50 text-white' : 'bg-white/20 text-gray-100'}`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white/10 rounded-lg p-3 flex items-center gap-2 text-sm text-gray-300">
              <Loader2 className="animate-spin" size={16} /> در حال فکر کردن...
            </div>
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 bg-black/30 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
          placeholder="پیام خود را بنویسید..."
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="bg-blue-500/50 hover:bg-blue-500/70 text-white p-2 rounded-lg transition-colors disabled:opacity-50"
        >
          <Send size={20} />
        </button>
      </div>
    </GlassPanel>
  );
}
