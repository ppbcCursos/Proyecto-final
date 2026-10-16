<script lang="ts">
  let { name, size = 18 }: { name: string; size?: number } = $props()
  const paths: Record<string, string> = {
    chat: 'M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-6 3V6a2 2 0 0 1 2-2ZM7 9h10M7 13h6',
    folder: 'M3 7V5a2 2 0 0 1 2-2h5l3 3h6a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7ZM3 9h18',
    book: 'M12 5C9 3 5 3 2 4v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-3-1-7-1-10 1Zm0 0v15',
    globe: 'M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0ZM16 12a4 9 0 1 1-8 0 4 9 0 0 1 8 0ZM3 12h18',
    file: 'M14 2H5a1 1 0 0 0-1 1v18a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V8l-6-6Zm0 0v6h6M8 12h8M8 16h8',
    calendar: 'M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2ZM7 3v4M17 3v4M3 11h18M7 15h2M13 15h2',
    check: 'm5 12 4 4L19 6',
    search: 'M17.5 10.5a7 7 0 1 1-14 0 7 7 0 0 1 14 0ZM16 16l5 5',
    users: 'M13 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM2 21v-3a7 7 0 0 1 14 0v3M16 4a4 4 0 0 1 0 8m4 9v-3a7 7 0 0 0-3-6',
    external: 'M14 3h7v7m0-7L10 14M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5',
    clock: 'M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0ZM12 7v5l3 2',
    arrow: 'M12 19V5m-6 6 6-6 6 6',
    chevron: 'm9 5 7 7-7 7',
    info: 'M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0ZM12 11v6m0-10v.1',
    shield: 'm12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-5',
    close: 'm6 6 12 12M6 18 18 6',
    copy: 'M10 8h9a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2ZM16 8V3H3v13h5',
    download: 'M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5',
    refresh: 'M20 7v5h-5M4 17v-5h5M5 7a8 8 0 0 1 13-2l2 2M4 17l2 2a8 8 0 0 0 13-2',
  }
</script>

<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="icon"><path d={paths[name] || paths.info} /></svg>
