const path = require('path')

const bike_cont = require('./../controllers/bike_cont')
const user_cont = require('./../controllers/user_cont')

module.exports = app => {
    app.post('/bikes', bike_cont.newBike)

    app.all("*", (req,res,next) => {
        res.sendFile(path.resolve("./static/dist/index.html"))
    });
}