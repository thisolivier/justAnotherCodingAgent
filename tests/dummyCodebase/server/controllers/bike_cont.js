const mongoose = require('mongoose')
const Bike = mongoose.model("Bike")

module.exports = {
    newBike: (req, res) => {
        console.log('the body is', req.body)
        let newBike = new Bike(req.body)
        newBike.save(err => {
            if (err) {
                console.log("API error making a new bike", err)
                res.status(400).json(err)
            } else {
                console.log("Added a new bike called", req.body.name)
                res.status(200).json("All OK")
            }
        })
    },
    getAll: () => {},
    getOne: () => {},
    updateOne: () => {},
    delete: () => {}
}