var express = require('express')
var path = require('path')
var bodyParser = require('body-parser')
var mongoose = require('mongoose')

var app = express()
app.use(express.static(path.join(__dirname, './static/dist')))
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))


require(path.join(__dirname, './server/config/mongoose.js'))
require(path.join(__dirname, './server/config/routes.js'))(app)

app.listen(7654, ()=>{
    console.log("I live! My address is 7654")
})