<script lang="ts">
  import type { Book } from './types'
  let { book, large = false }: { book: Book; large?: boolean } = $props()
</script>

<div class:large class="book-cover" style:--cover={book.cover_color} aria-hidden="true">
  <span class="cover-author">{book.author}</span>
  <span class="cover-title">{book.title}</span>
  <span class="cover-publisher">{book.publisher}</span>
</div>

<style>
  .book-cover{width:47px;height:68px;flex-shrink:0;border-left:3px solid #ffffff24;border-radius:1px 3px 3px 1px;background:var(--cover);box-shadow:2px 3px 5px #253c3717;color:#fff8e9;overflow:hidden;position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:8px 5px;text-align:center;font-family:Georgia,serif}.book-cover::before,.book-cover::after{content:'';position:absolute;border:1px solid #edeacf55;border-radius:50%;height:60px;width:60px;left:12px;top:37px}.book-cover::after{left:-25px;top:31px}.cover-author{font-family:var(--sans);font-size:3px;letter-spacing:.25px;text-transform:uppercase;position:relative;z-index:1}.cover-title{font-size:8px;line-height:1.1;position:relative;z-index:1}.cover-publisher{font-family:var(--sans);font-size:2px;text-transform:uppercase;letter-spacing:.3px;position:relative;z-index:1}.large{width:185px;height:280px;border-left-width:7px;padding:31px 19px 20px;box-shadow:5px 8px 17px #253c3723}.large::before{width:190px;height:190px;left:47px;top:120px}.large::after{width:160px;height:160px;left:-60px;top:140px}.large .cover-author{font-size:9px;letter-spacing:1.4px}.large .cover-title{font-size:31px;line-height:1.15}.large .cover-publisher{font-size:7px;letter-spacing:1.7px;padding-top:12px;border-top:1px solid #ffffff50}
</style>
