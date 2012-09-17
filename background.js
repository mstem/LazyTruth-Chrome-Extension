/*
Event LISTENERS

background.js --> URL Tracking, Initial Message Receiving(deactivated after first run?? Or how does the background page work)
		We Want the message receiving to run once (but not sure whether background page is run when extension is loaded)

popup.js --> Message Passing for change in the User's option (asynchronous)

listener.js -->  N/A (although it calls all the event listener from listener2.js)
		Note: Button Event Listener is built in the create_button_ui function

listener2.js --> Button Event Listener (not sure if we should fetch from the API once, or remain active)
		ChangeParse (basically message passing parser for the OPTIONS)
*/

// Helper Function to log when the listener was created
// Used for background/Popup  --> Mainly URL Tracking event listener and Initial Message Listener
function trackListener(listenerName) {
	var d = new Date();
	var t = d.getTime();

	console.log(listenerName + ' was created at time: ' + t);
}

var tab_id;

function listen_gmail() {
	chrome.tabs.query({url: '*://mail.google.com/*'}, function(tabs) {
		// very serious mistake --> tab_id should be the result's ID, not the object itself
		
		if (tabs[0]) {
			tab_id = tabs[0].id;
		} else console.log('tab id must not exist');
	
		
	});
}

function listen_chrome() {
	chrome.tabs.onUpdated.addListener(function(tabId, info, tab) {
			//ensure that tab_id is properly set
			listen_gmail();
			if (tabId === tab_id) {
				chrome.tabs.executeScript(tab_id, {file: 'listener.js'});

				if (localStorage && localStorage.option === 'persistent') {
					console.log('localStorage is persistent execute AJAX protocol');
					chrome.tabs.executeScript(tab_id, {file: 'send.js'});
				}
			}
				
		});
}

function messageListener() {
	// Again, we are anticipating the sort of Messages that is being passed
	// and hence throw no exceptions/errors, if the user ever attempts to send messages around
	chrome.extension.onMessage.addListener(
		function(request, sender, sendResponse) {
			if (request.question) {
				sendResponse({answer: localStorage['option']});
			}
		}
	);
	console.log("Extension : I have told my option in localStorage to the tab");
}

window.onload = function() {
	trackListener('URL Change Listener');
	messageListener();
	trackListener('Initial Message Passing Listener');
	localStorage['option'] = 'choice'
	listen_chrome();
};
