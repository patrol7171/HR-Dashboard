
//*********************************************  Spinner/Loader  *********************************************
function start_img_task() {
	// add task status elements
	div = $('<div class="progress"><div></div><div></div><div>...</div><div>&nbsp;</div></div>');
	$('#progress').append(div);
	// send ajax POST request to start background job
	$.ajax({
		type: 'POST',
		url: '/getAllImagesTask',
		success: function(data, status, request) {
			status_url = request.getResponseHeader('Location');
			update_progress(status_url, div[0]);
		},
		error: function() {
			alert('An unexpected error with the home page images occurred');
			console.log('An unexpected error with the home page images occurred');			
		}
	});
}

function update_progress(status_url, status_div) {
	// send GET request to status URL
	$.getJSON(status_url, function(data) {
		// update UI			   
		$(status_div.childNodes[2]).text(data['status']);
		if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
			if ('result' in data) {		
				result = data['result'];
				// post results to index page						
				run_index_page(result);						
			}
			else {
				// something unexpected happened
				$(status_div.childNodes[3]).text('Result: ' + data['state']);
				alert('An unexpected error occurred--please reload page');
				
			}		
		}
		else {
			// rerun in 5 seconds
			setTimeout(function() {
				update_progress(status_url, status_div);
				console.log('Task is still going...'); //TESTING
			}, 5000);
		}
	});
}

function run_index_page(info) {
	// send ajax POST request to send results to index page
	$.ajax({
		type: 'POST',
		url: '/',
		data: JSON.stringify(info),
		contentType: 'application/json',
		success: function (data) {			
			window.location.href = "https://hr-dashboard1.herokuapp.com/"; //production-Heroku
			/* window.location.href = "http://127.0.0.1:5000/"; */ //localhost for local testing only		
		},
		error: function() {
			alert('An unexpected error occurred--unable to show home page');
		}
	});
}

function start_pageload_task(task_func, page) {
	// send ajax POST request to start checking background job
	$.ajax({
		type: 'POST',
		url: '/getPageImagesTask/'+task_func,
		success: function(data, status, request) {
			status_url = request.getResponseHeader('Location');
			verify_progress(status_url, page);
		},
		error: function() {
			alert('An unexpected error with starting the page load task occurred');
		}
	});
}

function verify_progress(status_url, page_name) {
	// send GET request to status URL
	$.getJSON(status_url, function(data) {
		if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
			if ('result' in data) {		
				result = data['result'];
				// remove loader/spinner class and post results to page	
				$( "#loading" ).removeClass("loader loader-clock is-active");			
				show_page(result, page_name);						
			}
			else {				
				alert('Result: ' + data['state'] + '-- Please reload page'); // something unexpected happened
			}		
		}
		else {
			// rerun in 4 seconds
			setTimeout(function() {
				verify_progress(status_url, page_name);
				console.log('Task is still going...'); //TESTING
			}, 4000);
		}
	});
}

function show_page(info, page_name) {
	// send ajax POST request to send results to page
	$.ajax({
		type: 'POST',
		url: '/'+page_name,
		data: JSON.stringify(info),
		contentType: 'application/json',
		success: function (data) {			
			location.reload();	
		},
		error: function() {
			alert('An unexpected error occurred--unable to show page');
		}
	});
}

function setVisible(selector, visible) {
	document.querySelector(selector).style.display = visible ? 'block' : 'none';
}


//*********************************************   2  *********************************************




//*********************************************  3  *********************************************




//*********************************************  4  *********************************************