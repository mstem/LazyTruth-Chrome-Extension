// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var button = document.getElementById('save');

// Helper Function to log when the listener was created
// Used for background/Popup  --> Mainly URL Tracking event listener and Initial Message Listener
// Note: background.js and popup.js don't share
function trackListener(listenerName) {
	var d = new Date();
	var t = d.getTime();

	console.log(listenerName + ' was created at time: ' + t);
}

//The function that will actually send the message to the tab
// The order seems counter intuitive, but it is called by
// SendTabId because of the asynchronous nature of chrome.tabs.query
function sendMessage(option, tabId) {
	if (chrome && chrome.tabs.sendMessage) {
		console.log('Google sendMessage activated');
		console.log('tabID is :' + tabId);
		console.log('option is this: ' + option); 
		chrome.tabs.sendMessage(tabId, {new_option : option});
	}
}

//The Main function that is called by storeLocal (which is triggered by click event)
function sendTabId(option_to_send) {
	var tabId;
	// Because tabs.query is asynchronous, we need to call the optionChange function
	// within chrome.tabs.query
	chrome.tabs.query({url:'*://mail.google.com/*'},
		function(tabs) {
			tabId = tabs[0].id;
			sendMessage(option_to_send, tabId);
	});
}

function storeLocal() {
	var option;
	var oldOption;
	// Here, we're deliberately acknowledging that the setting is
	// by default choice (user click the button)
	if (document.getElementById('persistent').checked) {
		option = 'persistent';
	} else option = 'choice';
	
	if (localStorage) { //check if localStorage exists and then actually store
		oldOption = localStorage['option']
		localStorage['option'] = option;
			
		console.log(oldOption);
		console.log(option);
		
		// If the old option isn't the same as new option, send Message
		// via sendTabId Function (includes initial case, when localStorage
		// has 'undefined' value for 'option')
		if (oldOption !== option) {
			sendTabId(option);
		}

	}
}

window.onload = function() {	
	button.onclick = storeLocal;
	trackListener('Local Option Listener');
};


//Not sure if checkBrowser function is every going to be used
function checkBrowser() {
	if (chrome) return 'chrome'
	// Firefox, IE equivalent goes here
}
