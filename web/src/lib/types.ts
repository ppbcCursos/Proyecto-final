export interface Book {
  id: string
  title: string
  author: string
  publisher: string
  publication_date: string
  genre: string
  language: string
  cover_color: string
  document_id: string
  fragment: string
  is_demo: boolean
  type?: 'record'
}

export interface EditorialDocument {
  id: string
  title: string
  publisher: string
  records: Book[]
  record_count: number
  is_demo: boolean
  type: 'document'
}

export interface Citation {
  record_id: string
  document_id: string
  label: string
  fragment: string
  is_demo: boolean
}

export interface Answer {
  id?: string
  question: string
  kind: 'books' | 'authors' | 'publishers' | 'no_data' | 'help' | 'preference'
  title: string
  text: string
  note: string
  as_of: string
  books: Book[]
  groups: { label: string; count: number; books: Book[] }[]
  citations: Citation[]
  reason: string | null
}

export interface Stats {
  as_of: string
  mode: string
  books: number
  authors: number
  publishers: string[]
  documents: number
  years: number[]
  months: { month: number; count: number; state: 'past' | 'partial' | 'future' }[]
}

export interface Source {
  id: string
  name: string
  kind: string
  url: string
  domain: string
  description: string
  limitation: string
}

export const MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
export function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(value + 'T12:00:00Z'))
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch('/api' + path, options)
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(typeof data.detail === 'string' ? data.detail : `No se pudo completar la consulta (${response.status}).`)
  }
  return response.json() as Promise<T>
}
