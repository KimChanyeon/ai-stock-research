import { onUnmounted } from 'vue'

type SSEHandlers = Record<string, (data: unknown) => void>

export function useSSE() {
  let es: EventSource | null = null

  function connect(url: string, handlers: SSEHandlers) {
    close()
    es = new EventSource(url)
    for (const [event, handler] of Object.entries(handlers)) {
      es.addEventListener(event, (e: MessageEvent) => {
        try {
          handler(JSON.parse(e.data))
        } catch {
          handler(e.data)
        }
      })
    }
    es.onerror = close
  }

  function close() {
    es?.close()
    es = null
  }

  onUnmounted(close)

  return { connect, close }
}
