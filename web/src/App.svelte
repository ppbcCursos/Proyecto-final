<script lang="ts">
  import { onMount, tick } from 'svelte'
  import Icon from './lib/Icon.svelte'
  import BookCover from './lib/BookCover.svelte'
  import ChatAnswer from './lib/ChatAnswer.svelte'
  import { api, MONTHS, formatDate, type Answer, type Book, type EditorialDocument, type Source, type Stats } from './lib/types'

  type Page = 'chat' | 'documentos' | 'fuentes'
  let page = $state<Page>('chat')
  let stats = $state<Stats | null>(null)
  let sources = $state<Source[]>([])
  let researchedOn = $state('2026-10-16')
  let loading = $state(true)
  let error = $state('')
  let messages = $state<Answer[]>([])
  let busy = $state(false)
  let draft = $state('')
  let pendingQuestion = $state('')
  let chatError = $state('')
  let month = $state(9)
  let year = $state(2026)
  let conversationEnd: HTMLDivElement | undefined = $state()
  let search = $state('')
  let catalogMonth = $state('')
  let publisher = $state('')
  let kind = $state<'record' | 'document' | 'all'>('record')
  let catalog = $state<(Book | EditorialDocument)[]>([])
  let catalogTotal = $state(0)
  let catalogLoading = $state(false)
  let catalogError = $state('')
  let catalogController: AbortController | undefined
  let searchTimer: ReturnType<typeof setTimeout>
  let dialog: HTMLDialogElement | undefined = $state()
  let selectedBook = $state<Book | null>(null)
  let selectedDocument = $state<EditorialDocument | null>(null)
  let detailLoading = $state(false)
  let detailError = $state('')
  let detailController: AbortController | undefined
  let notification = $state('')
  let notificationTimer: ReturnType<typeof setTimeout>
  const sectionNames: Record<Page, string> = { chat: 'Consultas', documentos: 'Documentos y registros', fuentes: 'Fuentes y cobertura' }
  const monthQuestion = () => `¿Qué libros se han publicado en ${MONTHS[month - 1].toLocaleLowerCase('es')} de ${year}?`
  const monthBooks = $derived(messages[0]?.kind === 'books' ? messages[0].books : [])
  const monthDays = $derived(monthBooks.map(book => Number(book.publication_date.slice(8))))
  const calendarOffset = $derived((new Date(Date.UTC(year, month - 1, 1)).getUTCDay() + 6) % 7)
  const calendarDays = $derived(new Date(Date.UTC(year, month, 0)).getUTCDate())
  const consultationYear = $derived(Number(stats?.as_of.slice(0, 4) || year))
  const consultationMonth = $derived(Number(stats?.as_of.slice(5, 7) || month))
  const ask = (message: string) => api<Answer>('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) })
  const readableError = (value: unknown) => value instanceof Error ? value.message : 'No se pudo conectar con el servidor.'

  async function loadApp() {
    loading = true; error = ''
    try {
      const [summary, research] = await Promise.all([api<Stats>('/stats'), api<{ items: Source[]; researched_on: string }>('/sources')])
      stats = summary; sources = research.items; researchedOn = research.researched_on
      year = summary.years.includes(2026) ? 2026 : summary.years[0] ?? Number(summary.as_of.slice(0, 4))
      month = year === Number(summary.as_of.slice(0, 4)) ? Math.max(1, Number(summary.as_of.slice(5, 7)) - 1) : 9
      messages = await Promise.all([monthQuestion(), `¿Qué autores han publicado en ${year} y qué libros?`, `¿Qué editoriales han publicado en ${year} y cuántos libros?`].map(ask))
      await loadCatalog()
    } catch (value) { error = readableError(value) }
    finally { loading = false }
  }
  function updatePage() { const hash = window.location.hash.slice(1); page = hash === 'documentos' || hash === 'fuentes' ? hash : 'chat' }
  onMount(() => {
    updatePage(); void loadApp(); window.addEventListener('hashchange', updatePage)
    return () => { window.removeEventListener('hashchange', updatePage); catalogController?.abort(); detailController?.abort(); clearTimeout(searchTimer); clearTimeout(notificationTimer) }
  })
  function navigate(next: Page) { page = next; window.location.hash = next; window.scrollTo({ top: 0, behavior: 'instant' }) }
  async function updatePeriod() {
    if (busy) return
    busy = true; chatError = ''
    try { messages = [await ask(monthQuestion()), ...messages.slice(1)] }
    catch (value) { chatError = readableError(value) }
    finally { busy = false }
  }
  async function sendQuestion(question: string) {
    question = question.trim(); if (!question || busy) return
    busy = true; pendingQuestion = question; draft = ''; chatError = ''
    try { const answer = await ask(question); messages = [...messages, { ...answer, id: crypto.randomUUID() }]; await tick(); conversationEnd?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }
    catch (value) { draft = question; chatError = readableError(value) }
    finally { busy = false; pendingQuestion = '' }
  }
  async function loadCatalog() {
    catalogController?.abort(); const controller = new AbortController(); catalogController = controller
    catalogLoading = true; catalogError = ''
    try { const response = await api<{ items: (Book | EditorialDocument)[]; total: number }>('/catalog?' + new URLSearchParams({ kind, search, month: catalogMonth, publisher }), { signal: controller.signal }); catalog = response.items; catalogTotal = response.total }
    catch (value) { if (!controller.signal.aborted) catalogError = readableError(value) }
    finally { if (!controller.signal.aborted) catalogLoading = false }
  }
  function scheduleSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(() => { void loadCatalog() }, 180) }
  function clearFilters() { search = ''; catalogMonth = ''; publisher = ''; void loadCatalog() }
  async function openRecord(id: string) {
    detailController?.abort(); const controller = new AbortController(); detailController = controller
    selectedBook = null; selectedDocument = null; detailLoading = true; detailError = ''; if (!dialog?.open) dialog?.showModal()
    try { selectedBook = await api<Book>('/books/' + encodeURIComponent(id), { signal: controller.signal }) }
    catch (value) { if (!controller.signal.aborted) detailError = readableError(value) }
    finally { if (!controller.signal.aborted) detailLoading = false }
  }
  async function openDocument(id: string) {
    detailController?.abort(); const controller = new AbortController(); detailController = controller
    selectedBook = null; selectedDocument = null; detailLoading = true; detailError = ''; if (!dialog?.open) dialog?.showModal()
    try { selectedDocument = await api<EditorialDocument>('/documents/' + encodeURIComponent(id), { signal: controller.signal }) }
    catch (value) { if (!controller.signal.aborted) detailError = readableError(value) }
    finally { if (!controller.signal.aborted) detailLoading = false }
  }
  function notify(text: string) { notification = text; clearTimeout(notificationTimer); notificationTimer = setTimeout(() => { notification = '' }, 3200) }
  async function copyReference(book: Book) {
    try { await navigator.clipboard.writeText(`${book.author}. ${book.title}. ${book.publisher}, ${book.publication_date}. ${book.id}. Registro ficticio de demostración.`); notify('Referencia copiada') }
    catch { notify('Selecciona el texto de la ficha para copiar la referencia.') }
  }
</script>

<svelte:head><title>Folio · {sectionNames[page]}</title><meta name="description" content="Consulta libros publicados en castellano por meses, autores y editoriales, con registros y fragmentos como evidencia. Catálogo de demostración." /></svelte:head>

<div class="app-layout">
  <aside class="sidebar">
    <a class="brand" href="#chat" aria-label="Folio, consultas"><span class="brand-icon"><Icon name="book" size={31} /></span>folio</a>
    <div class="brand-description">EL MES, ENTRE LÍNEAS</div>
    <nav aria-label="Navegación principal"><a href="#chat" class:active={page === 'chat'} aria-current={page === 'chat' ? 'page' : undefined}><Icon name="chat" />Consultas</a><a href="#documentos" class:active={page === 'documentos'} aria-current={page === 'documentos' ? 'page' : undefined}><Icon name="folder" />Documentos<span class="nav-count">{stats ? stats.books + stats.documents : '—'}</span></a><a href="#fuentes" class:active={page === 'fuentes'} aria-current={page === 'fuentes' ? 'page' : undefined}><Icon name="globe" />Fuentes y cobertura</a></nav>
    <div class="side-label">UNA PREGUNTA, UN CAMINO</div>
    <button class="side-question" onclick={() => { navigate('chat'); void sendQuestion(monthQuestion()) }} disabled={busy || loading}>Lo publicado este mes</button>
    <button class="side-question" onclick={() => { navigate('chat'); void sendQuestion(`¿Qué autores han publicado en ${year} y qué libros?`) }} disabled={busy || loading}>Las voces del año</button>
    <button class="side-question" onclick={() => { navigate('chat'); void sendQuestion(`¿Qué editoriales han publicado en ${year} y cuántos libros?`) }} disabled={busy || loading}>El mapa editorial</button>
    <div class="sidebar-bottom"><div class="scope-mini"><strong>El catálogo, a día de hoy</strong>Castellano · España · Muestra 2026<br /><span class="dot"></span> Consulta: {stats ? formatDate(stats.as_of) : 'conectando…'}</div><div class="profile"><span class="avatar">L</span><div><strong>Mi biblioteca</strong>Espacio local de demostración</div></div></div>
  </aside>
  <main class="workspace">
    <header class="app-topbar"><div class="breadcrumbs"><span>Mi biblioteca</span><Icon name="chevron" size={13} /><strong>{sectionNames[page]}</strong></div><div class="topbar-meta"><span class="pill demo"><span class="dot"></span>Datos ficticios</span>{#if stats}<span class="consultation-date"><Icon name="calendar" size={14} />{formatDate(stats.as_of)}</span>{/if}</div></header>
    <div class="app-content">
      {#if loading}<div class="loading-state" role="status"><span class="spinner"></span><h1>Abriendo el catálogo…</h1><p>Conectando con los registros de tu biblioteca.</p></div>
      {:else if error}<div class="error-state" role="alert"><Icon name="info" size={30} /><h1>No hemos podido abrir el catálogo.</h1><p>{error}</p><p>Comprueba que el servidor Python está disponible en el puerto 8000.</p><button class="btn primary" onclick={() => void loadApp()}><Icon name="refresh" size={15} />Volver a intentar</button></div>
      {:else if stats}
        {#if page === 'chat'}
          <div class="page-heading"><div><div class="eyebrow">Una conversación con el catálogo</div><h1>Hablemos de libros.</h1><p>Explora lo publicado en castellano, mes a mes. Con el dato y su origen.</p></div><span class="pill green"><Icon name="check" size={13} />Catálogo de muestra</span></div>
          <div class="chat-layout"><div class="chat-primary">
            <div class="scope-bar"><Icon name="calendar" size={15} /><label class="sr-only" for="chat-month">Mes de consulta</label><select id="chat-month" value={month} disabled={busy} onchange={e => { month = Number(e.currentTarget.value); void updatePeriod() }}>{#each MONTHS as name, index}<option value={index + 1} disabled={year === consultationYear && index + 1 > consultationMonth}>{name}{year === consultationYear && index + 1 > consultationMonth ? ' · futuro' : ''}</option>{/each}</select><span class="scope-separator">/</span><label class="sr-only" for="chat-year">Año de consulta</label><select id="chat-year" value={year} disabled={busy} onchange={e => { year = Number(e.currentTarget.value); if (year === consultationYear && month > consultationMonth) month = consultationMonth; void updatePeriod() }}>{#each stats.years as value}<option {value}>{value}</option>{/each}</select><span class="pill green"><Icon name="check" size={12} />Solo publicados</span></div>
            <div class="conversation" id="conversation">{#each messages as answer, index (answer.id || index)}<ChatAnswer {answer} onOpen={openRecord} />{/each}{#if pendingQuestion}<div class="pending-answer" role="status"><div class="user-message"><div class="user-bubble">{pendingQuestion}</div><span class="avatar">L</span></div><span class="spinner small"></span>Consultando los registros…</div>{/if}<div bind:this={conversationEnd}></div></div>
            <div class="suggestions" aria-label="Consultas de ejemplo"><button disabled={busy} onclick={() => void sendQuestion(`¿Qué libros se han publicado en ${MONTHS[consultationMonth - 1].toLowerCase()} de ${consultationYear}?`)}>El mes en curso</button><button disabled={busy} onclick={() => void sendQuestion(`¿Qué autores han publicado en ${year} y qué libros?`)}>Autores de {year}</button><button disabled={busy} onclick={() => void sendQuestion('No me preguntes por fechas futuras a la del día de la consulta.')}>Limitar las fechas a hoy</button></div>
            <form class="composer" onsubmit={e => { e.preventDefault(); void sendQuestion(draft) }}><label class="sr-only" for="chat-input">Pregunta al catálogo</label><textarea id="chat-input" bind:value={draft} placeholder="Pregunta por un mes, una autoría o una editorial…" maxlength="1000" rows="2" required disabled={busy} onkeydown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); e.currentTarget.form?.requestSubmit() } }}></textarea><div class="composer-bottom"><span><Icon name="shield" size={13} />Solo respuestas respaldadas por el catálogo</span><button class="send-button" type="submit" disabled={busy || !draft.trim()} aria-label="Enviar consulta"><Icon name="arrow" size={19} /></button></div></form>
            {#if chatError}<p class="inline-error" role="alert">{chatError} Puedes volver a enviar la consulta.</p>{/if}<p class="composer-help">Consulta guiada · Ctrl + Intro para enviar · Sin llamadas a modelos externos</p>
          </div><aside class="chat-context" aria-label="Contexto del catálogo">
            <div class="context-card"><div class="eyebrow">El mes en perspectiva</div><h2>{MONTHS[month - 1]} de {year}</h2><div class="calendar-heading"><span>{monthBooks.length} novedades registradas</span><Icon name="calendar" size={14} /></div><div class="calendar">{#each ['L', 'M', 'X', 'J', 'V', 'S', 'D'] as day}<b>{day}</b>{/each}{#each Array(calendarOffset) as _}<span></span>{/each}{#each Array(calendarDays) as _, index}<span class:release={monthDays.includes(index + 1)} class:future={year === consultationYear && month === consultationMonth && index + 1 > Number(stats.as_of.slice(8))}>{index + 1}</span>{/each}</div><p>{year === consultationYear && month === consultationMonth ? `Cobertura parcial: hasta el día ${Number(stats.as_of.slice(8))}.` : monthBooks.length ? 'Cada fecha señalada tiene una ficha editorial que la respalda.' : 'No hay registros de este mes en la muestra.'}</p></div>
            <div class="context-card"><div class="eyebrow">Tu catálogo disponible</div><div class="context-stat"><span>Libros publicados</span><strong>{stats.books}</strong></div><div class="context-stat"><span>Autores y autoras</span><strong>{stats.authors}</strong></div><div class="context-stat"><span>Editoriales</span><strong>{stats.publishers.length}</strong></div></div>
            <div class="context-card"><h2>Del dato a la respuesta</h2><div class="context-step"><span>1</span><div><strong>Consultamos</strong>El catálogo disponible.</div></div><div class="context-step"><span>2</span><div><strong>Comprobamos</strong>Idioma y fecha de publicación.</div></div><div class="context-step"><span>3</span><div><strong>Citamos</strong>El registro y su fragmento.</div></div></div><p class="side-note">Leer también es saber de dónde viene cada historia.<small>Folio · Consulta con fuentes</small></p>
          </aside></div>
        {:else if page === 'documentos'}
          <div class="page-heading"><div><div class="eyebrow">Los datos detrás de cada respuesta</div><h1>La biblioteca de las respuestas.</h1><p>Busca los documentos y registros que Folio puede utilizar en sus consultas.</p></div><a class="btn" href="/api/export.csv" download="folio-catalogo-demo.csv" title="Exportar todos los registros del catálogo"><Icon name="download" size={15} />Exportar CSV</a></div>
          <div class="stats-row">{#each [{ count: stats.books, label: 'Registros de libros', icon: 'book' }, { count: stats.documents, label: 'Documentos de origen', icon: 'file' }, { count: stats.authors, label: 'Autores y autoras', icon: 'users' }, { count: stats.publishers.length, label: 'Editoriales', icon: 'folder' }] as stat}<div class="stat-box"><div><strong>{stat.count}</strong><span>{stat.label}</span></div><Icon name={stat.icon} size={22} /></div>{/each}</div>
          <div class="catalog-tabs" aria-label="Tipo de contenido">{#each [{ value: 'all', label: 'Todo', count: stats.books + stats.documents }, { value: 'record', label: 'Registros', count: stats.books }, { value: 'document', label: 'Documentos', count: stats.documents }] as tab}<button class:active={kind === tab.value} aria-pressed={kind === tab.value} onclick={() => { kind = tab.value as typeof kind; void loadCatalog() }}>{tab.label}<span>{tab.count}</span></button>{/each}</div>
          <form class="catalog-toolbar" role="search" onsubmit={e => e.preventDefault()}><label class="search-input"><Icon name="search" size={16} /><span class="sr-only">Buscar título, autoría, editorial o identificador</span><input type="search" bind:value={search} oninput={scheduleSearch} placeholder="Buscar por título, autor, editorial o identificador…" autocomplete="off" /></label><label class="sr-only" for="catalog-month">Mes de publicación</label><select id="catalog-month" value={catalogMonth} onchange={e => { catalogMonth = e.currentTarget.value; void loadCatalog() }}><option value="">Todos los meses</option>{#each stats.years as availableYear}{#each MONTHS as name, index}{#if availableYear < consultationYear || index < consultationMonth}<option value={`${availableYear}-${String(index + 1).padStart(2, '0')}`}>{name} {availableYear}{availableYear === consultationYear && index + 1 === consultationMonth ? ' · parcial' : ''}</option>{/if}{/each}{/each}</select><label class="sr-only" for="catalog-publisher">Editorial</label><select id="catalog-publisher" value={publisher} onchange={e => { publisher = e.currentTarget.value; void loadCatalog() }}><option value="">Todas las editoriales</option>{#each stats.publishers as value}<option {value}>{value}</option>{/each}</select></form>
          <div class="catalog-results"><span role="status" aria-live="polite">{catalogLoading ? 'Buscando…' : `${catalogTotal} ${catalogTotal === 1 ? 'resultado' : 'resultados'} · Castellano`}</span><button class="text-button" onclick={clearFilters}>Limpiar filtros</button></div>
          {#if catalogError}<div class="inline-error" role="alert">{catalogError}<button class="text-button" onclick={() => void loadCatalog()}>Reintentar</button></div>{:else if catalog.length}<div class="table-scroll" class:fetching={catalogLoading} aria-busy={catalogLoading}><table class="catalog-table"><thead><tr><th scope="col">Título / documento</th><th scope="col">Editorial</th><th scope="col">Publicación</th><th scope="col">Tipo</th><th scope="col">Estado</th></tr></thead><tbody>{#each catalog as item (item.id)}<tr><td><div class="record-cell"><span class="file-symbol" class:document={item.type === 'document'}><Icon name={item.type === 'document' ? 'folder' : 'file'} size={17} /></span><div><button class="record-title" onclick={() => item.type === 'document' ? void openDocument(item.id) : void openRecord(item.id)}>{item.title}</button><small>{item.id} · {item.type === 'document' ? `${item.record_count} fichas editoriales` : item.author}</small></div></div></td><td>{item.publisher}</td><td>{item.type === 'document' ? '2026 · varias fechas' : formatDate(item.publication_date)}</td><td>{item.type === 'document' ? 'Documento' : 'Registro'}</td><td><span class="pill" class:green={item.type !== 'document'}>{item.type === 'document' ? 'Ficticio' : 'Publicado'}</span></td></tr>{/each}</tbody></table></div>{:else if !catalogLoading}<div class="empty-state"><Icon name="search" size={29} /><h2>No encontramos ese registro.</h2><p>Prueba otro término o elimina algún filtro. No se completan datos que no constan.</p><button class="btn" onclick={clearFilters}>Limpiar filtros</button></div>{/if}
          <div class="information-note"><Icon name="info" size={15} /><span>Registros y documentos ficticios, almacenados en tu catálogo local. Los documentos reúnen las fichas de cada editorial; la fecha se comprueba en cada registro.</span></div>
        {:else}
          <div class="page-heading"><div><div class="eyebrow">El origen, el alcance y sus límites</div><h1>Las fuentes también se leen.</h1><p>Fuentes editoriales reales investigadas. Revisión: {formatDate(researchedOn)}.</p></div><span class="pill"><Icon name="globe" size={14} />{sources.length} fuentes reales</span></div>
          <div class="research-banner"><Icon name="info" size={19} /><div><strong>Fuentes reales investigadas; catálogo de demostración.</strong><p>Estos enlaces no respaldan los libros inventados de la aplicación. Sus registros y fragmentos son ficticios. No hay sincronización automática con las editoriales.</p></div></div>
          <div class="sources-layout"><div>{#each sources as source (source.id)}<article class="real-source"><span class="source-monogram" aria-hidden="true">{source.name === 'Editorial Anagrama' ? 'A' : source.name === 'Ediciones Siruela' ? 'S' : 'P'}</span><div class="real-source-main"><div class="real-source-title"><h2>{source.name}</h2><a href={source.url} target="_blank" rel="noopener noreferrer">Visitar fuente<Icon name="external" size={12} /></a></div><div class="source-domain">{source.domain} · {source.kind}</div><p>{source.description}</p><div class="source-limitation"><Icon name="info" size={13} />{source.limitation}</div></div></article>{/each}<div class="information-note"><Icon name="book" size={16} /><span>El criterio es comprobar fecha e idioma en la ficha de cada edición, conservar el documento y su fragmento y contar una sola vez cada registro. Un anuncio no acredita una publicación.</span></div></div><aside><div class="context-card"><div class="eyebrow">Cobertura de la demo</div><h2>{consultationYear}, hasta hoy</h2><div class="coverage-months">{#each stats.months as item}<span class:partial={item.state === 'partial'} class:unavailable={item.state === 'future'} title={item.state === 'future' ? 'Fecha futura: no consta' : `${item.count} registros de la muestra`}>{MONTHS[item.month - 1].slice(0, 3).toLowerCase()}</span>{/each}</div><div class="coverage-legend"><span><i></i>Periodo consultable</span><span><i class="partial"></i>Mes parcial · hasta hoy</span><span><i class="unavailable"></i>Futuro · no consta</span></div><div class="coverage-rules"><h3>Qué entra en el recuento</h3><p>Ediciones en castellano con fecha explícita igual o anterior a la consulta.</p><h3>Qué significa un mes vacío</h3><p>No hay registros en esta muestra. No permite concluir que no se publicaron libros.</p></div></div><div class="context-card"><h2>Un alcance transparente</h2><p>{stats.books} registros ficticios de {stats.publishers.length} editoriales. No representa todo el mercado.</p><button class="text-button" onclick={() => navigate('documentos')}>Ver qué datos tenemos →</button></div></aside></div>
        {/if}
        <footer class="app-footer"><span><Icon name="shield" size={12} />Catálogo ficticio · Castellano · Consulta: {formatDate(stats.as_of)}</span><span>{stats.books} registros · {stats.documents} documentos</span></footer>
      {/if}
    </div>
  </main>
</div>

<dialog bind:this={dialog} aria-labelledby="detail-heading"><div class="dialog-header"><h2 id="detail-heading">{selectedBook ? `${selectedBook.id} · Ficha del libro` : selectedDocument ? `${selectedDocument.id} · Documento de origen` : 'Detalle del catálogo'}</h2><button class="close-dialog" onclick={() => dialog?.close()} aria-label="Cerrar detalle"><Icon name="close" size={20} /></button></div><div class="dialog-body">
  {#if detailLoading}<div class="modal-state" role="status"><span class="spinner"></span>Abriendo el registro…</div>{:else if detailError}<p class="inline-error" role="alert">{detailError}</p>
  {:else if selectedBook}<div class="record-layout"><div class="cover-area"><BookCover book={selectedBook} large /><p>Portada de demostración</p></div><div class="record-summary"><span class="pill green"><span class="dot"></span>Publicado antes de la consulta</span><h3>{selectedBook.title}</h3><p class="record-author">{selectedBook.author}</p><dl class="record-fields"><div><dt>Publicación</dt><dd>{formatDate(selectedBook.publication_date)}</dd></div><div><dt>Editorial</dt><dd>{selectedBook.publisher}</dd></div><div><dt>Idioma</dt><dd>{selectedBook.language}</dd></div><div><dt>Género</dt><dd>{selectedBook.genre}</dd></div><div><dt>Registro interno</dt><dd>{selectedBook.id}</dd></div><div><dt>Ámbito</dt><dd>España · Libro impreso</dd></div></dl><button class="btn primary" onclick={() => selectedBook && void copyReference(selectedBook)}><Icon name="copy" size={14} />Copiar referencia</button></div></div><div class="record-evidence"><div class="record-evidence-heading"><Icon name="file" size={15} />Fragmento que respalda la ficha<span class="pill green">Texto ficticio</span></div><blockquote>«{selectedBook.fragment}»</blockquote><div class="record-evidence-footer"><span>{selectedBook.document_id} · Entrada {selectedBook.id}</span><button class="text-button" onclick={() => selectedBook && void openDocument(selectedBook.document_id)}>Ver documento de origen →</button></div></div>
  {:else if selectedDocument}<span class="pill">Documento ficticio · {selectedDocument.record_count} fichas</span><h3 class="document-heading">{selectedDocument.title}</h3><p class="document-description">Documento de demostración conservado en la base local. Estas son todas sus entradas.</p>{#each selectedDocument.records as book (book.id)}<div class="document-entry"><button class="text-button" onclick={() => void openRecord(book.id)}><Icon name="file" size={13} />{book.id} · {book.title}<Icon name="external" size={11} /></button><blockquote>«{book.fragment}»</blockquote></div>{/each}<p class="document-description">Contenido inventado; no procede de las fuentes editoriales reales investigadas.</p>{/if}
</div></dialog>
{#if notification}<div class="toast" role="status">{notification}</div>{/if}
