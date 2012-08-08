/*
Few Notes: Unclear as to what we should do with some foreign characters,
one problem for instance �--> this character doesn't seem to be taken care of

Bankruptcy 101 doesn't work (Can't be sure as to why)

So malicious viral e-mail could take advantage of this

But in general, the client-side nesting seems pretty thorough and working (at least for all the e-mails)
Matt has sent me.
*/
var countryDomain = 'ac|ad|ae|af|ag|ai|al|am|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cw|cx|cy|cz|||||de|dj|dk|dm|do|dz||ec|ee|eg|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sk|sl|sm|sn|so|sr|ss|st|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|za|zm|zw';

function sanitize_html(html) {	
	// Note that regex3 is deprecated -> we found bugs (some emails have lots of &gt as a style)
	// regex4 will take care of all escaped characters, including those of regex 3

	var new_string = html.outerHTML; //always get outer HTML
	var regex1 = /<[\w\W\n]+?>/g;  //Non-greedy tag fetcher with global 
	var regex2 = /[\n]/g;	     // empty space replacer
	var regex3 = /&gt;/g;			// Non-greedy tag for any EMail <, > characters (for nesting)
	var regex4 = /&[\w\W]+?;/g;	// Non-greedy tag for any HTML escape characters
	var regex5 = /[\w]+.(?=com|org|edu)/g; // Email Matching for > (for nesting)


	new_string = new_string.replace(regex1, '');
	new_string = new_string.replace(regex2, ' ');
	//new_string = new_string.replace(regex3, '>');
	new_string = new_string.replace(regex5, '>'); 
	new_string = new_string.replace(regex4, '');

	return new_string;
}

///////////////////////////////////////////////
// Helper Functions
///////////////////////////////////////////////

/*
The Viral determining function is currently just length
We can look for ways to improve upon this (we are relying on the length of the viral email)

We should always keep in mind that if a user has javascript disabled, what will we do?
We should have server-side backup (i.e. cutting up even more characters) filtering


Current methodology: put indicators next to potentially splittable places (such as '>')
potentially splittable places --> next to e-mail addresses 

Matt's Suggestion: (___@____.com)


Potentially can look for 
(i) Number of links in part of an email
(ii) Styling
(iii) ... (Can't think of anymore but room for improvement)

*/
function score_function(part) {
	return part.length
}

// Note the flexibility of JavaScript
// As function names are objects !!
// In my mind, list = array (at least in Python)
function max_score(list, f) {
	var part_index;
	var highest_index=0;
	var highest_score=0;

	for (part_index=0; part_index < list.length; part_index++) {
		console.log(f(list[part_index]));
		if (f(list[part_index]) >= f(list[highest_index])) {
			highest_index = part_index;
			highest_score = f(list[part_index]);
		}
		console.log('highest index is: ' + highest_index);
	}
	
	return highest_index;
}
		
// The main function that's splitting the body according to '>' characters, appearing at end of an email address
// (Only the From/To of emails have this --> Although GMail's email formatting completely ignores this
// i.e.) Gmail --> On Tuesday, July 31st, Someone Wrote:
function body_nest(body) {
	var new_body;
	var body_part;

	new_body = body.split(/>/g);
	console.log(new_body[0]);
	
	return new_body[max_score(new_body, score_function)];
}

///////////////////////////////////////////////

function myResponse(result) {
	// No need to check for the existence of UI --> for if there weren't any UI component
	// (i.e. the particular email isn't a viral email OR the page itself doesn't contain any email)
	// there would have been no call to the Server to begin with
	//var extension = document.getElementById('canvas_frame').contentDocument.getElementsByClassName('contextual_extension')[0];
	console.log(result);
	var iframe = document.getElementById('canvas_frame').contentDocument;
	var source_icon = iframe.getElementsByClassName('lazytruth-icon')[0];
	var debunk_text = iframe.getElementsByClassName('lazytruth-text')[0];
	var link = iframe.getElementsByClassName('lazytruth-link')[0];
	
	if (result.matched === true) { // and there was a match
		//source_icon.setAttribute('src', result.source_icon_url);
		var textLength = result.fact_text.length
		debunk_text.innerHTML = result.fact_text.substr(0, textLength -1);
		console.log(result.detail_url);
		link.innerHTML = result.detail_url;
	} else {
		debunk_text.innerHTML = 'I am sorry that the information you sent is currently not available. Please email us at ';
		link.setAttribute('href', 'mailto:checkme@lazytruth.com');
		link.innerHTML = 'checkme@lazytruth.com';
		// return (False, [])
	}
}


///////////////////////////////////////////////
// Actual Function that's calling the API
///////////////////////////////////////////////
function body_log() {
	var body;
	var body_length;
	var match_url;
	var array = document.getElementById('canvas_frame').contentDocument.getElementsByClassName('ii gt adP adO');
	var last_email_index = array.length;


	// Instead of sending non-existent data to server, we can handle client-side and see whether
	// or not if there exists any data to send at all
	if (last_email_index !== 0) {
		last_email = array[last_email_index - 1];

		body = sanitize_html(last_email); // eliminate the html_tags
		body_length = body.length;

		//console.log(body);
		//console.log(body_nest(body));
	
		//Please Note that our current client-side filtering is really dependent on the (nested email) scoring function
		viral_body = body_nest(body);
		console.log(viral_body);

		match_url = 'http://lazytruth.media.mit.edu/data/api/0.1/match/';
		$.ajax({
			type: "POST",
			url: match_url,
			data: {'text' : viral_body},
			dataType: 'json',
			success: myResponse
		});

		return viral_body;
	} else console.log('No request to server because there is no email to fetch information from');
}

// really a measure for automatically activating AJAX to lazytruth server
// we can add logic (via a new function) when to execute body_log
// Note: to add logic, even in choice(button-case), we need to add LOGIC in create_button_ui
body_log();
