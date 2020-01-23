const express = require('express')
const app = express()

app.set('view engine', 'ejs')
app.use(express.stattic('public'))

app.get('/', (req, res) => {
    res.send("Hello")
})

server = app.listen(3000)

const io = require('socket.io')(server)

io.on('connect', (socket) => {
    console.log('New user connected')
})