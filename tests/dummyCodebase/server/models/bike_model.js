const mongoose = require('mongoose')
const Schema = mongoose.Schema

const BikeSchema = mongoose.Schema({
    name: {type: String, required: true},
    desc: {type: String, required: true},
    price: {type: Number, required: true},
    location: {type: String, required: true},
    image: {type: String, required: true},
    user: { type: Schema.Types.ObjectId, ref: 'User'}
}, {timestamps: true})

mongoose.model("Bike", BikeSchema)