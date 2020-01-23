// var app4 = new Vue({
//   el: '#app-4',
//   data: {
//     suggestions: [],
//     seen:true,
//     unseen:false
//   },
//   //Adapted from https://stackoverflow.com/questions/36572540/vue-js-auto-reload-refresh-data-with-timer
//   created: function() {
//     this.fetchSuggestionList();
//     this.timer = setInterval(this.fetchSuggestionList, 10000);
//   },
//   methods: {
//     fetchSuggestionList: function() {
//       axios
//         .get('/suggestions/')
//         .then(response => (this.suggestions = response.data.suggestions))
//       console.log(this.suggestions)
//       this.seen=false
//       this.unseen=true
//     },
//     cancelAutoUpdate: function() { clearInterval(this.timer) }
//   },
//   beforeDestroy() {
//     this.cancelAutoUpdate();
//   }
// })

var pusher = new Pusher('47917f39c6cb18036d35',{
  cluster: 'us3'
});
var socketId = null;
pusher.connection.bind('connected', function() {
    socketId = pusher.connection.socket_id;
});

var my_channel = pusher.subscribe('a_channel');
var config = { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } };
new Vue({
el: "#app",
data: {
  'message': '',
  'conversations': []
},
mounted() {
  this.getConversations();
  this.listen();
},
methods: {
  sendMessage() {
    axios.post('/conversation/', this.queryParams({message: this.message}), config)
      .then(response => {
        this.message = '';
      });
  },
  getConversations() {
    axios.get('/conversations/').then((response) => {
      this.conversations = response.data;
      this.readall();
    });  
  },
  listen() {
    my_channel.bind("an_event", (data)=> {
      this.conversations.push(data);
      axios.post('/conversations/'+ data.id +'/delivered/', this.queryParams({socket_id: socketId}));
    })
    my_channel.bind("delivered_message", (data)=> {
      for(var i=0; i < this.conversations.length; i++){
        if (this.conversations[i].id == data.id){
          this.conversations[i].status = data.status;
        }
      }
    })
  },
  readall(){
    for(var i=0; i < this.conversations.length; i++){
      if(this.conversations[i].status=='Sent'){
          axios.post('/conversations/'+ this.conversations[i].id +'/delivered/');
      }
    }
  },
  queryParams(source) {
    var array = [];
    for(var key in source) {
        array.push(encodeURIComponent(key) + "=" + encodeURIComponent(source[key]));
    }
    return array.join("&");
    }
  }
});