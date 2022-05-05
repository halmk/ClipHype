var note = new Vue({
  el: '#notes',
  delimiters: ['[[', ']]'],

  data: {
    notes: [],
  },

  methods: {
    setClasses: function() {
      this.notes.forEach(note => {
        note.bg = 'bg-' + note.status;
        note.btn = 'btn-' + note.status;
      });
    }
  },

  mounted() {
    this.notes = notes;
    this.setClasses();
  }
});
