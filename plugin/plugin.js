// ==UserScript==
// @name     Bookoski
// @version  2.1
// ==/UserScript==

nameArticle = document.getElementById("firstHeading").getElementsByTagName('i')[0].innerHTML;

function addButton(text) {
  cssObj = {color : '#0645ad'}
  let button = document.createElement('a'), btnStyle = button.style
  button.innerHTML = text
	button.href = "http://bookoski.com/book/"+nameArticle
  document.getElementById("siteSub").innerHTML += ".&nbsp&nbsp&nbsp&nbsp"
  document.getElementById("siteSub").appendChild(button) //firstHeading
  
  Object.keys(cssObj).forEach(key => btnStyle[key] = cssObj[key])
  
  return button
}

addButton('Bookoski🡕');
