const express = require("express")
const fs = require("fs")
const path =require("path")

const {neon} = require("@neondatabase/serverless")
require("dotenv").config()

const sql = neon(process.env.DATABASE_URL)

sql`select version()`
.then(result=>console.log(result))

const app = express()
const port = 3000
app.listen(port)
console.log("Server started..")


app.use(express.json())
app.use(express.urlencoded({extended:true}))




app.get("/",(req,res)=>{
   res.send("Shopping Cart API - Neon DB")
    
})



app.post("/shopper",async (req,res)=>{
   try{
      const shopper = await sql`INSERT INTO shoppers (name, user_name) VALUES (${req.body.name},${req.body.user_name}) returning *`

      if (shopper.length == 0)
         res.send("Error. Something went wrong..")

      res.send(shopper[0])

   }catch(err){
      console.log(err)
      res.send(err)
   }

})


app.get("/shopper",async (req,res)=>{
   try{
      const shoppers = await sql`SELECT * from shoppers`
      res.send(shoppers)

   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.get("/shopper/:user_name",async (req,res)=>{
   try{
      let shopper = await sql`SELECT * from shoppers where user_name = ${req.params.user_name}`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")

      const items = await sql`SELECT * from cart_items where shopper = ${req.params.user_name}`

      shopper = shopper[0]
      shopper.items= items

      res.send(shopper)

   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.delete("/shopper/:user_name",async (req,res)=>{
   try{
      const shopper = await sql`DELETE from shoppers where user_name = ${req.params.user_name} returning *`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")

      const items = await sql`DELETE from cart_items where shopper = ${req.params.user_name} returning *`
      msg = `Removed shopper with user_name ${req.params.user_name} along with ${items.length} cart items`
      res.send(msg)


   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.post("/addToCart",async (req,res)=>{
   try{
      let shopper = await sql`SELECT * from shoppers where user_name = ${req.body.shopper}`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")

      const item = await sql`INSERT INTO cart_items(item_name,price,qty,shopper) values(
      ${req.body.name},${req.body.price},${req.body.qty},${req.body.shopper}
      ) returning *`


      
      res.send(item)


   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.post("/removeFromCart",async (req,res)=>{
   try{
      let shopper = await sql`SELECT * from shoppers where user_name = ${req.body.shopper}`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")

      const item = await sql`DELETE FROM cart_items where shopper = ${req.body.shopper} and item_name = ${req.body.name} returning *`
      if (item.length == 0)
         return res.send("Error. Item does not exist..")

      res.send(item)


   }catch(err){
      console.log(err)
      res.send(err)
   }

})


app.post("/updateCart",async (req,res)=>{
   try{
      let shopper = await sql`SELECT * from shoppers where user_name = ${req.body.shopper}`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")


      const item = await sql`UPDATE cart_items set qty = ${req.body.qty} where shopper = ${req.body.shopper} and item_name = ${req.body.name} returning *`
      if (item.length == 0)
         return res.send("Error. Item does not exist..")

      if(item[0].qty == 0)
         await sql`DELETE from cart_items where shopper = ${req.body.shopper} and item_name = ${req.body.name}`
     
      res.send(item)




   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.post("/checkout/:shopper",async (req,res)=>{
   try{
      let shopper = await sql`SELECT * from shoppers where user_name = ${req.params.shopper}`

      if (shopper.length == 0)
         return res.send("Error. Shopper does not exist..")


      const items = await sql`DELETE from cart_items where shopper = ${req.params.shopper} returning *`
     
      let total = 0
      console.log(items)
      items.forEach(item=>{total+=parseInt(item.qty)*parseFloat(item.price)})

      msg = `${req.params.shopper} has checked out. Their total is $${total}`

      res.send(msg)



   }catch(err){
      console.log(err)
      res.send(err)
   }

})

app.get("/summary",async (req,res)=>{
   try{
      const shoppers = await sql`SELECT * from shoppers`
      for (let s of shoppers)
         s.items =  await sql`SELECT * from cart_items where shopper = ${s.user_name}`
      
      res.send(shoppers)

   }catch(err){
      console.log(err)
      res.send(err)
   }
})