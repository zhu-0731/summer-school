// Vue 应用主文件
const { createApp, ref, onMounted } = Vue

const app = createApp({
    setup() {
        // 响应式数据
        const messages = ref([])
        const userInput = ref('')
        const chatMode = ref('single')
        const isLoading = ref(false)

        // 发送消息
        const sendMessage = async () => {
            if (!userInput.value.trim() || isLoading.value) return

            const input = userInput.value
            userInput.value = ''
            isLoading.value = true

            // 添加用户消息
            messages.value.push({
                content: input,
                type: 'user',
                timestamp: new Date().toLocaleTimeString()
            })

            try {
                // 发送API请求
                const endpoint = chatMode.value === 'single' ? '/api/single_chat' : '/api/multi_chat'
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: input })
                })

                const data = await response.json()

                // 添加AI响应
                messages.value.push({
                    content: data.response,
                    type: 'ai',
                    timestamp: new Date().toLocaleTimeString()
                })

                // 自动滚动到底部
                scrollToBottom()
            } catch (error) {
                console.error('Error:', error)
                messages.value.push({
                    content: '发生错误，请稍后重试。',
                    type: 'ai',
                    timestamp: new Date().toLocaleTimeString()
                })
            } finally {
                isLoading.value = false
            }
        }

        // 清空历史记录
        const clearHistory = async () => {
            try {
                await fetch('/api/clear', { method: 'POST' })
                messages.value = []
            } catch (error) {
                console.error('Error clearing history:', error)
            }
        }

        // 加载历史记录
        const loadHistory = async () => {
            try {
                const response = await fetch('/api/history')
                const data = await response.json()
                if (data.history) {
                    messages.value = data.history.map(msg => ({
                        content: msg.user || msg.assistant,
                        type: msg.user ? 'user' : 'ai',
                        timestamp: msg.timestamp
                    }))
                    scrollToBottom()
                }
            } catch (error) {
                console.error('Error loading history:', error)
            }
        }

        // 自动滚动到底部
        const scrollToBottom = () => {
            setTimeout(() => {
                const chatMessages = document.querySelector('.chat-messages')
                chatMessages.scrollTop = chatMessages.scrollHeight
            }, 100)
        }

        // 处理按键事件
        const handleKeyPress = (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                sendMessage()
            }
        }

        // 组件挂载后加载历史记录
        onMounted(() => {
            loadHistory()
        })

        return {
            messages,
            userInput,
            chatMode,
            isLoading,
            sendMessage,
            clearHistory,
            handleKeyPress
        }
    }
})

// 挂载应用
app.mount('#app')
