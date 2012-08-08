// called in listener.js for consolidating all the functions that are called
// when the script is run --> working
// seems like jquery isn't particularly favored in asynchronous calls

/*
UI Functions

Format
******************
** File_in_extension || First_function_called
				First_function_called_by_first
(corresponding reading		....
in Google Extension		Last_function_called_by_first
Documentation or 
brief explanation of
what the part is doing)	
			Second_function_called
				First_function_by_second
				....
				Last_Function_called_by_second
			Third
				...
				
** Next File_	     || ...

...
*******************
Indentation indicates the Scope of the functions
Functions on same indentation level lives in the same Scope

(I) WHEN PAGE HAS CHANGED (ASYNCHRONOUSLY/SYNCHRONOUSLY)  --> Defined as Local Change

Involved parts: listener.js, listener2.js, background.js
***************
** listener.js  ||  Inject_Div function
		    	Create_UI--> base frame created by Justin/Stefan
			initialize_button_ui
		    
** listener2.js ||  	initialize_button_ui --> (i) get localStorage data from the extension, then (ii) create or NOT create Button UI
(logic)

** background.js||  		messageListener --> responds with a dictionary {'option' : persistent | choice}
(message passing)

** listener2.js ||		create_button_ui --> Helper function that creates actual HTML elements
(actual UI change)

** listener.js 	||  Inject Div injects the 'target'
***************

(II) PAGE HAS NOT CHANGED (i.e. user is contemplating to change the Global Behavior) --> Defined as Global Change

Involved parts: popup.js, listener2.js
******************
** popup.js	||  storeLocal  --> when the user clicks the radiobutton and saves
(message passing)	sendTabId --> gets the Id of the TAB which gmail is loaded (note: asynchronous)
				sendMessage  --> actually sends the message to content_script listener2.js

** listener2.js || 		changeParse  --> Event Listener to Message Passing
(message passing)			
(UI change)				changeOption --> actually deletes the UI if necessary
******************

*/


// ASYNCHRONOUS FUNCTIONS !!!! (sendMessage)

// Currently Listener Problem (Port Establishment) --> Resolved (Listener creation timing issue)
function changeParse() {
	chrome.extension.onMessage.addListener(
		function(request, sender, sendResponse) {
			var new_option;
		
			// We can do something like this b/c we know
			// we will always get new_option parameter, if a request is sent
			new_option = request.new_option;
			
			// We want to change Option whenever we receive a message
			changeOption(new_option)
		}
	);
}

// This function really belongs in this javascript file
// since the button UI creation is really determined by the Option set by user
function changeOption(option) {
	// we want to delete the button_ui if the option is not persistent
	if (option === 'persistent') {
		console.log("delete_button_ui(); should have been triggered!");
		delete_button_ui();
	} else {
		//console.log('recreate_button_ui() has been triggered!');
		recreate_button_ui();
	}
	//console.log("Tab : I have been notified of the change!");
}

function initialize_button_ui(target_div) {
	// Function takes no input and outputs True if the initial extension option is choice
	// meaning that we would like to create the button (hence True)
	// Else, the choice must be persistent and thus we don't want the button

	console.log('Tab : I am going to ask the Extension, for the first load time!');

	chrome.extension.sendMessage({question:'tellme'}, function(response) {
		// True here means that we want the button ui to be created
		// Note that when first called after installation(meaning response.answer === undefined)
		// The button ui is still going to be created
		
		// Boolean really doesn't work because sendMessage is asynchronous
		console.log('I got this answer from localStorage:' + response.answer);
		if (response.answer !== 'persistent') {
			create_button_ui(target_div);
			console.log('button will be Created');
		} else {
			console.log('button will NOT be created');
		}
	});
}

// For recreating/deleting button ui, because we are using asynchronous calls, let's make sure that 
// deleting/recreating happens only Once
function delete_button_ui() {
	var buttonEle = document.getElementById('canvas_frame').contentDocument.getElementById('lazytruth-button');
	
	if (buttonEle) {
		var parentNode = buttonEle.parentNode;

		parentNode.removeChild(buttonEle);
	}
}

// recreationg doesn't seem to be working too well
// Javascript console freezes --> which means infinite loop
// or something unusual --> can reuse console after loading/reloading
function recreate_button_ui() {
	var contextualExt = document.getElementById('canvas_frame').contentDocument.getElementsByClassName('contextual_extension')[0];
	var len = contextualExt.childNodes.length -1;
	if (contextualExt.childNodes[len].id !=='lazytruth-button') {
		create_button_ui(contextualExt);	
	} else console.log('Google multiple asynchronous requests');
}

function create_button_ui(new_div) {
	//Intially new_div is created below, but modified code so that
	// I can add the button ui on top of the existing UI
	
	// Initially commented out the extraction part
	//var new_div = document.createElement('div');

	// Button for testing fetching the body of the email
	body_fetcher = document.createElement('BUTTON');
	body_fetcher.setAttribute('id', 'lazytruth-button');
	button_text = document.createTextNode('Fetch the Body');
	body_fetcher.appendChild(button_text);
	
	body_fetcher.addEventListener("click", body_log)
	new_div.appendChild(body_fetcher);

	return new_div
}

