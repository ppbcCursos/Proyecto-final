<script lang="ts">
  import Icon from './Icon.svelte'
  import type { Citation } from './types'
  let { citations, onOpen }: { citations: Citation[]; onOpen: (id: string) => void } = $props()
</script>

{#snippet quote(citation: Citation)}
  <div class="source-quote">
    <button onclick={() => onOpen(citation.record_id)}><Icon name="file" size={12} />{citation.label}<Icon name="external" size={11} /></button>
    <blockquote>«{citation.fragment}»</blockquote>
    <span class="source-id">{citation.document_id} · Registro ficticio</span>
  </div>
{/snippet}

<div class="evidence">
  <div class="evidence-label"><Icon name="file" size={13} />Fuentes · {citations.length} {citations.length === 1 ? 'registro' : 'registros'} de demostración</div>
  <div class="evidence-grid">{#each citations.slice(0, 2) as citation (citation.record_id)}{@render quote(citation)}{/each}</div>
  {#if citations.length > 2}
    <details><summary>Ver los {citations.length - 2} registros restantes y sus fragmentos</summary><div class="evidence-grid">{#each citations.slice(2) as citation (citation.record_id)}{@render quote(citation)}{/each}</div></details>
  {/if}
</div>
