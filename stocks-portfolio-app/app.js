let users = JSON.parse(userContent)
const stocks = JSON.parse(stockContent)
console.log(users)
console.log(stocks)

const portfolioDiv = document.querySelector('#listPortfolio')
const list = document.querySelector('.UserList ul')

/* Generates the user list by looping through the users array and creating a list item for each user.
   Clears the list first to prevent duplicates. Stores the user's id as a data attribute on the list item. */
function generateUserList() {
    list.innerHTML = ''
    users.forEach(user => {
        const li = document.createElement('li')
        li.textContent = user.user.lastname + ", " + user.user.firstname
        li.dataset.id = user.id
        list.appendChild(li)
    })
}

/* Fills the user form with the selected user's information.
   Also stores the user's id in the hidden input field so it can be retrieved when Save or Delete is clicked. */
function fillUserForm(selectedUser) {
    document.getElementById('userID').value = selectedUser.id
    document.getElementById('firstname').value = selectedUser.user.firstname
    document.getElementById('lastname').value = selectedUser.user.lastname
    document.getElementById('address').value = selectedUser.user.address
    document.getElementById('city').value = selectedUser.user.city
    document.getElementById('email').value = selectedUser.user.email
}

/* Generates the portfolio list for the selected user by looping through their portfolio array.
   Creates a paragraph for the symbol, a paragraph for the number of shares, and a View button for each stock.
   Resets the portfolio div first to prevent duplicates when switching between users. */
function generatePortfolio(selectedUser) {
    portfolioDiv.innerHTML = '<h3>Symbol</h3><h3># Shares</h3><h3>Actions</h3>'
    selectedUser.portfolio.forEach(stock => {
        const symbol = document.createElement('p')
        symbol.textContent = stock.symbol
        const owned = document.createElement('p')
        owned.textContent = stock.owned
        const button = document.createElement('button')
        button.textContent = 'View'
        button.dataset.symbol = stock.symbol
        portfolioDiv.appendChild(symbol)
        portfolioDiv.appendChild(owned)
        portfolioDiv.appendChild(button)
    })
}

/* Fills the stock details section with the selected stock's information.
   Also sets the stock logo image using the stock's symbol to find the correct SVG file in the logos directory. */
function fillStockDetails(selectedStock) {
    document.getElementById('logo').src = 'logos/' + selectedStock.symbol + '.svg'
    document.getElementById('stockName').textContent = selectedStock.name
    document.getElementById('stockSector').textContent = selectedStock.sector
    document.getElementById('stockIndustry').textContent = selectedStock.subIndustry
    document.getElementById('stockAddress').textContent = selectedStock.address
}

/* Clears all sections of the page including the user form, portfolio list and stock details.
   Called when a user is deleted to reset the page to its initial state. */
function clearSections() {
    document.getElementById('userID').value = ''
    document.getElementById('firstname').value = ''
    document.getElementById('lastname').value = ''
    document.getElementById('address').value = ''
    document.getElementById('city').value = ''
    document.getElementById('email').value = ''

    /* Resets the portfolio div to just the headers to clear out any previous stocks. */
    portfolioDiv.innerHTML = '<h3>Symbol</h3><h3># Shares</h3><h3>Actions</h3>'

    document.getElementById('logo').src = ''
    document.getElementById('stockName').textContent = ''
    document.getElementById('stockSector').textContent = ''
    document.getElementById('stockIndustry').textContent = ''
    document.getElementById('stockAddress').textContent = ''
}

/* Generate the user list on page load */
generateUserList()

/* Listens for clicks on the user list. Uses event delegation to handle clicks on any list item.
   Retrieves the user's id from the clicked element's dataset, finds the matching user and fills in their details. */
list.addEventListener('click', function(event) {
    const id = event.target.dataset.id
    if (!id) return
    const selectedUser = users.find(user => user.id == id)
    if (!selectedUser) return
    fillUserForm(selectedUser)
    generatePortfolio(selectedUser)
})

/* Listens for clicks on the portfolio div. Uses event delegation to handle clicks on any View button.
   Retrieves the stock symbol from the clicked button's dataset, finds the matching stock and fills in its details. */
portfolioDiv.addEventListener('click', function(event) {
    if (event.target.tagName === 'BUTTON') {
        const symbol = event.target.dataset.symbol
        const selectedStock = stocks.find(stock => stock.symbol === symbol)
        if (!selectedStock) return
        fillStockDetails(selectedStock)
    }
})

/* Listens for clicks on the Save button. Retrieves the user's id from the hidden input field,
   finds the matching user, updates their information with the current form values and regenerates the user list. */
document.querySelector('#btnSave').addEventListener('click', function(event) {
    event.preventDefault()
    const id = document.getElementById('userID').value
    if (!id) return
    const selectedUser = users.find(user => user.id == id)
    if (!selectedUser) return
    selectedUser.user.firstname = document.getElementById('firstname').value
    selectedUser.user.lastname = document.getElementById('lastname').value
    selectedUser.user.address = document.getElementById('address').value
    selectedUser.user.city = document.getElementById('city').value
    selectedUser.user.email = document.getElementById('email').value
    generateUserList()
})

/* Listens for clicks on the Delete button. Retrieves the user's id from the hidden input field,
   removes the user from the users array, clears all sections and regenerates the user list. */
document.querySelector('#btnDelete').addEventListener('click', function(event) {
    event.preventDefault()
    const id = document.getElementById('userID').value
    if (!id) return
    users = users.filter(user => user.id != id)
    clearSections()
    generateUserList()
})