var app = new Vue({
  el: '#apitest',
  delimiters: ['[[', ']]'],

  data: {
  },
  methods: {
    request: function() {
      axios.get(googleapirequest_url)
        .then(function(response) {
          console.log(response);
        });
    }
  },
  mounted() {
  }
});
