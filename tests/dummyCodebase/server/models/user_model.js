const mongoose = require("mongoose")
const Schema = mongoose.Schema

const UserSchema = mongoose.Schema({
    name1: {type: String, required: true},
    name2: {type: String, required: true},
    email: {type: String, required: true},
    pass: {type: String, required: true},
    bikes: [{ type: Schema.Types.ObjectId, ref: 'Bike' }]
}, {timestamps: true})

mongoose.model("User", UserSchema)

// // Hey, this creates a new user
// const User = mongoose.model("User")
// let newUser = new User()
// newUser.name1 = "Bob"
// newUser.name2 = "Elvenhouse"
// newUser.email = "guest"
// newUser.pass = "guest"
// newUser.save(err => {console.log("New user created. Any errors?", err)})