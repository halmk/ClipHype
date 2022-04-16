var app = new Vue({
  el: '#notes',
  delimiters: ['[[', ']]'],

  data: {
    notes: [],
  },
  mounted() {
    this.notes = notes;
    this.notes.forEach(note => {
      note.bg = 'bg-' + note.status;
      note.btn = 'btn-' + note.status;
    });
  }
});
