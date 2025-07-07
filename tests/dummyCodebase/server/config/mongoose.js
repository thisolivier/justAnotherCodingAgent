const mongoose = require('mongoose')
const fs = require('fs')
const path = require('path')
const models_path = path.join(__dirname, './../models')

mongoose.Promise = global.Promise
mongoose.connect('mongodb://localhost/bikes', {useMongoClient: true})


// All JS files in the models directory should be required into this file
// We check that each file ends in js, only requiring it if it does
// We use readdirSync so that if the models change, the requirements are updated
fs.readdirSync(models_path).forEach(file => {
    if(file.toLowerCase().includes(".js")){
        require(path.join(models_path, file))
    }
})