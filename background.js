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

// Google Analytics Code
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-22982865-1']);
//_gaq.push(['_trackPageview']);

(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = 'https://ssl.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();


function logButtonClick(buttonId) {
	_gaq.push(['_trackEvent', buttonId, 'clicked']);
}

function logButtonImpression(buttonId) {
	_gaq.push(['_trackEvent', buttonId, 'viewed']);
}
// End Google Analytics Code

// Helper Function to log when the listener was created
// Used for background/Popup  --> Mainly URL Tracking event listener and Initial Message Listener
function trackListener(listenerName) {
	var d = new Date();
	var t = d.getTime();

	console.log(listenerName + ' was created at time: ' + t);
}

var gmail_tabs;

function listen_gmail() {
	chrome.tabs.query({url: '*://mail.google.com/*'}, function(tabs) {
		// very serious mistake --> tab_id should be the result's ID, not the object itself
		for (i=0; i < tabs.length; ++i) {
			gmail_tabs = tabs[0].id;	
		}
		
	});
}

function listen_chrome() {
	chrome.tabs.onUpdated.addListener(function(tabId, info, tab) {
			//ensure that tab_id is properly set
			listen_gmail();
			
			if (tabId == gmail_tabs) {
				chrome.tabs.executeScript(tabId, {file: 'listener.js'});
				chrome.tabs.executeScript(tabId, {file: 'send.js'});
				chrome.tabs.executeScript(tabId, {file: 'listener2.js'});
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
			if (request.buttonClick) {
				console.log("Button Click Message from Content Script");
				logButtonClick(request.buttonClick);
				sendResponse({answer: "Button Click Logged"});
			}
			if (request.buttonImpression) {
				console.log("Button Impression Message from Content Script");
				success = logButtonImpression(request.buttonImpression);
				if (success) {sendResponse({answer: "Button Impression Failed"});}
				else {sendResponse({answer: "Button Impression Logged"});}
			}
		}
	);
}


function onInstall() {
    console.log("Extension Installed");
	chrome.tabs.create({url: "http://www.lazytruth.com/?page_id=78"});
}

function onUpdate() {
    console.log("Extension Updated");
}

function getVersion() {
    var details = chrome.app.getDetails();
    return details.version;
}

window.onload = function() {
	trackListener('URL Change Listener');
	messageListener();
	trackListener('Initial Message Passing Listener');
	localStorage['option'] = 'choice'
	listen_chrome();
	// Check if the version has changed.
	var currVersion = getVersion();
	var prevVersion = localStorage['version']
	if (currVersion != prevVersion) {
    // Check if we just installed this extension.
	if (typeof prevVersion == 'undefined') {
      onInstall();
    } else {
      onUpdate();
    }
    localStorage['version'] = currVersion;
  }
};
