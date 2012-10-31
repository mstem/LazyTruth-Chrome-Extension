function create_ui() {
	var new_div;
	var inner_div;
	var link;
	var debunkText;
	var header;
	var srcIcon;
	
	// Initially commented out the extraction part
	new_div = document.createElement('div'); 		
  
	debunkText = document.createElement("span");
	debunkText.innerHTML = "&nbsp;";
	debunkText.setAttribute('class', 'lazytruth-text');

	// default picture is the snopes picture
	srcIcon = document.createElement("img"); 
	//srcIcon.setAttribute('src','http://lazytruth.media.mit.edu/media/sourceicons/snopes.png'); 
	srcIcon.setAttribute('style','float:left;padding-top:1.5em;padding-left:1em;');
	srcIcon.setAttribute('class', 'lazytruth-icon');

	// For empty container, below if statement is simply ignored, we'll always assume there's a detail_url
	// WHICH MEANS that there's always an answer to the fact
	link = document.createElement('a');
	link.setAttribute('href', '<www.matching_detailed_url.com> or "mailto:checkme@lazytruth.com"');  
	link.setAttribute('style','font-weight:bold;padding-left:5px;font-size:1.1em;color:blue;display:none;');
	link.innerHTML = "Link to Appear if url exists or checkme@lazytruth.com";
	link.setAttribute('class', 'lazytruth-link');

	debunkText.appendChild(link);
	
	header = document.createElement('span');
	header.innerHTML = "LazyTruth Says:";
	header.setAttribute('style','font-weight:bold;padding-bottom:0.25em;display:block;');

	inner_div = document.createElement('div');
	inner_div.setAttribute('style','padding:1em;margin-left:4em;background-color:#EFEFEF;border:1px solid;');
	
	new_div.appendChild(srcIcon);
	inner_div.appendChild(header);
	inner_div.appendChild(debunkText);

	detButtonCreation(inner_div,'initialize');

	new_div.appendChild(inner_div);

	// Button for testing fetching the body of the email, Inheriting create_button_ui from listener2.js
	// so if initialize button ui says that I should create button
	new_div.setAttribute('class', 'contextual_extension');
	new_div.style.fontSize="0.8em"; 

	return new_div;
}


// The Function that actually inserts the UI, lives in check_frames function to insert
// Few ISSUES --> DEBUGGING IS telling me that either MY Logic is wrong or something's not right
function inject_div(div) {
	console.log('injecting div');
	var target = create_ui();


	// The next line will do 2 things
	// (i) get localStorage information
	// (ii) based on (i), create the UI
	console.log(target);

	if (div && (div.parentNode.childNodes.length < 3)) {	//avoid duplicates, b/c onUpdated event triggers script twice
		//trackTimer('origina UI to be inserted');		
		div.parentNode.insertBefore(target, div);
	} 
	
}

///////////////////////////////////////////////////////
// Frame Checking and UI Insertion MACRO_LOGIC --> 
// By MACRO_LOGIC : I'm simply checking for existence of target
// cf) MICRO_LOGIC: in Button UI generation
///////////////////////////////////////////////////////

/*	
 Few Bugs with frame checking  --->  

(i) If you load an email page initially (that initial email probably won't contain the lazytruth):
	You can go back to inbox and check again

(ii) the if statement where it checks for the 'gA gt ac5' div class is buggy in the javascript console
but the injection isn't showing any bugs --> I am confident and can assure you that this is not a problem
though I'm curious why this is happening

--->there were in fact more than one 'gA gt ac5' within iframe

*/
function check_frames() {
	var frame = document.getElementById(':rr');
	if (frame) {


		// Turns out the latter part isn't such a good way to check frames (as it would be true even if
		// the element didn't exist at all--> that's because it's an element!!!
		// Even with frame.contentDocument --> Not so successful after a while (returns just the div tag)

		var array = frame.getElementsByClassName('ii gt adP adO');
		if (array.length !== 0) {			
			var last_email_index = array.length;

			if (last_email_index !== 0) {
				last_email = array[last_email_index - 1];
				var body = last_email.outerHTML;
				console.log('BODY OF '+body);
				var forward = false;
				if (body.search('---- Forwarded message ----') > -1) {
					console.log('TRUE 1');
					forward = true;
				}
				if (body.search('---- Original message ----') > -1) {
					console.log('TRUE 2');
					forward = true;
				}
				if (body.search('Begin forwarded message:') > -1) {
					console.log('TRUE 3');
					forward = true;
				}		
				var subjectArray = frame.getElementsByClassName('ha');
				var subject = subjectArray[0].innerHTML;
				console.log('SUBJECT OF '+subject);
				if (subject.search('Fwd') > -1) {
					console.log('TRUE 4');
					forward = true;
				}
				if (subject.search('FWD') > -1) {
					console.log('TRUE 5');
					forward = true;
				}
				if (subject.search('Welcome to LazyTruth!') > -1) {
					console.log('Welcome Email Detected');
					forward = true;
				}
				if (!forward) {
					return;
				}
			}


			var target_div = frame.getElementsByClassName('gA gt ac5');
			//console.log(target_div);
			// This was the key --> there were in fact more than one 'gA gt ac5' within iframe
			var target_div_index = target_div.length -1;
			
			inject_div(target_div[target_div_index]);

		} 

	} 
};
///////////////////////////////////////

check_frames();
changeParse();
// Only Functions that need to be run when the script is executed



///////////////////////////////////////
// Currently Unused Function

function response(extracted_text) {
	// response sent to the server (our database) --> should return, in JSON FORMAT, [detail_url, fact_text, img_source, source_name]
	if (matching_info_exists) {
		//do this
		// and return (True, [detail_url, fact_text, img_source, source_name])
	} else {
		// return (False, [])
	}	
}
//////////////////////////////////////

// Interval Checking is unncessary as we do URL Update Checking --> catches even AJAX behavior, overactiveness fixed
//var lazyInterval = setInterval(check_frames, 5000);

