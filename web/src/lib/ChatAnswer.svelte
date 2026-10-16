<script lang="ts">
  import Icon from './Icon.svelte'
  import BookCover from './BookCover.svelte'
  import Evidence from './Evidence.svelte'
  import { formatDate, type Answer } from './types'
  let { answer, onOpen }: { answer: Answer; onOpen: (id: string) => void } = $props()
</script>

<article class="exchange">
  <div class="user-message"><div class="user-bubble">{answer.question}</div><span class="avatar" aria-label="Tú">L</span></div>
  <div class="assistant-answer">
    <span class="assistant-mark" aria-hidden="true">f</span>
    <div class="assistant-name">Folio <span>{answer.kind === 'no_data' ? 'Sin registros válidos' : answer.citations.length ? 'Con fuentes' : 'Consulta guiada'}</span></div>
    {#if answer.kind === 'no_data'}
      <div class="no-data"><span class="no-data-symbol"><Icon name={answer.reason === 'fecha_futura' ? 'clock' : 'search'} /></span><h3>{answer.title}</h3><p>{answer.text}</p><div class="no-evidence"><strong><Icon name="file" size={13} />Fuentes de esta respuesta</strong>{answer.reason === 'fecha_futura' ? 'La fecha solicitada es posterior al día de consulta.' : answer.reason === 'sin_registros' ? 'No hay registros para el periodo solicitado en esta muestra. Esto no implica que no se hayan publicado libros en el mercado.' : 'No se han encontrado registros suficientemente relacionados con la consulta.'}<br />Sin fuentes que permitan justificar una respuesta. No se han añadido datos.<br />Fecha de consulta: {formatDate(answer.as_of)}.</div></div>
    {:else}
      <p>{answer.text}</p>
      {#if answer.kind === 'books'}
        <div class="book-grid">{#each answer.books as book (book.id)}<button class="book-card" onclick={() => onOpen(book.id)} aria-label={`Ver registro de ${book.title}`}><BookCover {book} /><span class="book-info"><strong>{book.title}</strong><span>{book.author}</span><small>{formatDate(book.publication_date)} · {book.publisher}</small></span></button>{/each}</div>
      {:else if answer.kind === 'authors'}
        <table class="answer-table"><thead><tr><th scope="col">Autoría</th><th scope="col">Libros publicados</th></tr></thead><tbody>{#each answer.groups as group (group.label)}<tr><td><strong>{group.label}</strong><small>{group.count} libros</small></td><td>{#each group.books as book (book.id)}<button class="inline-book" onclick={() => onOpen(book.id)}>{book.title}</button><span class="publication-month">{formatDate(book.publication_date)}</span><br />{/each}</td></tr>{/each}</tbody></table>
      {:else if answer.kind === 'publishers'}
        <div class="publisher-list">{#each answer.groups as group (group.label)}<div class="publisher-item"><span>{group.label}</span><span class="bar-track" aria-hidden="true"><i style:width={`${group.count / Math.max(...answer.groups.map(g => g.count)) * 100}%`}></i></span><strong>{group.count}</strong></div>{/each}<div class="sumline"><span>Total de títulos únicos</span><strong>{answer.groups.reduce((total, group) => total + group.count, 0)} libros</strong></div></div>
      {/if}
    {/if}
    <p class="answer-note">{answer.note}</p>
    {#if answer.citations.length}<Evidence citations={answer.citations} {onOpen} />{/if}
  </div>
</article>
