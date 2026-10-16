import type { Answer, Book, Citation, EditorialDocument } from './types'

export interface Libro {
  registro_id: string
  titulo: string
  autor: string
  editorial: string
  fecha_publicacion: string
  idioma: string
  genero: string
}
export interface Fuente {
  documento_id: string
  documento: string
  registro_id: string
  fragmento: string
  similitud: number
  datos_ficticios: boolean
}
export interface Respuesta {
  pregunta: string
  pregunta_contextualizada: string
  respuesta: string
  estado: 'respondido' | 'no_consta' | 'preferencia'
  motivo: string | null
  fecha_consulta: string
  modelo_usado: boolean
  fuentes: Fuente[]
  libros: Libro[]
  autores: { nombre: string; cantidad: number; libros: Libro[] }[]
  editoriales: { nombre: string; cantidad: number; libros: Libro[] }[]
  aviso: string
}
export interface ListadoDocumentos {
  documentos: {
    id: string
    titulo: string
    editorial: string
    archivo: string
    cantidad_registros: number
    registros: Libro[]
    fragmentos: Fuente[]
    datos_ficticios: boolean
  }[]
  registros: Libro[]
  total_documentos: number
  total_registros: number
  fecha_consulta: string
  aviso: string
}

// These adapters change field names only. Bibliographic facts and fragments
// always come from /api; the colour is decorative, as in the original mockup.
export function bookView(libro: Libro, fuentes: Fuente[] = []): Book {
  const fuente = fuentes.find(item => item.registro_id === libro.registro_id)
  const colours = ['#7c866a', '#b78966', '#698c91', '#c09b69', '#8d8a77', '#607d6c', '#7c9297', '#b39073', '#8e827d', '#a6a071', '#7f8799', '#b19d76']
  const number = Number(libro.registro_id.replace(/\D/g, '')) || 1
  return {
    id: libro.registro_id, title: libro.titulo, author: libro.autor,
    publisher: libro.editorial, publication_date: libro.fecha_publicacion,
    genre: libro.genero, language: libro.idioma,
    cover_color: colours[(number - 1) % colours.length],
    document_id: fuente?.documento_id ?? '', fragment: fuente?.fragmento ?? '',
    is_demo: fuente?.datos_ficticios ?? true, type: 'record',
  }
}

export function answerView(response: Respuesta): Answer {
  const kind = response.estado === 'no_consta' ? 'no_data'
    : response.estado === 'preferencia' ? 'preference'
    : response.autores.length ? 'authors' : response.editoriales.length ? 'publishers' : 'books'
  const groups = response.autores.length ? response.autores : response.editoriales
  const citations: Citation[] = response.fuentes.map(fuente => ({
    record_id: fuente.registro_id, document_id: fuente.documento_id,
    label: `${fuente.documento} · ${fuente.registro_id}`,
    fragment: fuente.fragmento, is_demo: fuente.datos_ficticios,
  }))
  return {
    id: crypto.randomUUID(), question: response.pregunta, kind,
    title: response.estado === 'no_consta' ? 'No consta en los datos.' : '',
    text: response.estado === 'respondido' ? response.respuesta.split('\n')[0] : response.respuesta,
    note: response.aviso, as_of: response.fecha_consulta,
    books: response.libros.map(book => bookView(book, response.fuentes)),
    groups: groups.map(group => ({ label: group.nombre, count: group.cantidad, books: group.libros.map(book => bookView(book, response.fuentes)) })),
    citations, reason: response.motivo,
  }
}

export function catalogView(response: ListadoDocumentos, kind: 'all' | 'record' | 'document'): (Book | EditorialDocument)[] {
  const fragments = response.documentos.flatMap(doc => doc.fragmentos)
  const books = response.registros.map(book => bookView(book, fragments))
  const documents: EditorialDocument[] = response.documentos.map(doc => ({
    id: doc.id, title: doc.titulo, publisher: doc.editorial,
    records: doc.registros.map(book => bookView(book, doc.fragmentos)),
    record_count: doc.cantidad_registros, is_demo: doc.datos_ficticios, type: 'document',
  }))
  return kind === 'record' ? books : kind === 'document' ? documents : [...books, ...documents]
}
