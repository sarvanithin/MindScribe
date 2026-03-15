interface ChatBubbleProps {
    role: 'ai' | 'user'
    text: string
    isTyping?: boolean
}

export default function ChatBubble({ role, text, isTyping }: ChatBubbleProps) {
    return (
        <div className={`bubble-row ${role}`}>
            <div className={`bubble-avatar ${role}`}>
                {role === 'ai' ? 'AI' : 'You'}
            </div>
            <div className={`bubble ${role}`}>
                {isTyping ? (
                    <div className="typing-dots">
                        <span /><span /><span />
                    </div>
                ) : (
                    text
                )}
            </div>
        </div>
    )
}
