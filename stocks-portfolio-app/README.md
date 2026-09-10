# Stocks Portfolio App

A vanilla JavaScript single-page app for browsing users and their stock portfolios, built without any framework to demonstrate direct DOM manipulation, event handling, and working with static JSON data sources.

## What it does

- Renders a list of users from a JSON data file and lets you select one to view/edit their profile
- Displays each selected user's stock portfolio (symbol, shares owned) in a dynamically generated table
- Populates and clears a user-edit form driven entirely by vanilla DOM APIs (`createElement`, `dataset`, `querySelector`) — no external libraries beyond a CSS reset
- Includes per-company stock logos and a formatted stock reference dataset

## Tech

HTML5, CSS3, vanilla JavaScript (ES6+)

## Run

Open `index.html` in a browser, or serve the folder with any static file server.

## Status

Complete coursework assignment: user list, portfolio view, and editable user form are all functional against the bundled static dataset.
