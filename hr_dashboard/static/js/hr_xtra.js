
//*********************************************  Loader/Spinner  *********************************************
function start_img_task() {
	// add task status elements
	console.log('hello!')
	div = $('<div class="progress"><div></div><div></div><div>...</div><div>&nbsp;</div></div>');
	$('#progress').append(div);

	// create a progress bar
	var nanobar = new Nanobar({
		bg: '#8DFF33',
		target: div[0].childNodes[0]
	});

	// send ajax POST request to start background job
	$.ajax({
		type: 'POST',
		url: '/getAllImagesTask',
		success: function(data, status, request) {
			status_url = request.getResponseHeader('Location');
			update_progress(status_url, nanobar, div[0]);
		},
		error: function() {
			alert('An unexpected error occurred');
		}
	});
}


function update_progress(status_url, nanobar, status_div) {
	// send GET request to status URL
	$.getJSON(status_url, function(data) {
		// update UI
		percent = parseInt(data['current'] * 100 / data['total']);
		nanobar.go(percent);
		$("#percent").text(percent + '%');			   
		$(status_div.childNodes[2]).text(data['status']);
		if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
			if ('result' in data) {
				// show index page		
				console.log(data);
				run_index_page(data);
				$("#page-body").show();
			}
			else {
				// something unexpected happened
				$(status_div.childNodes[3]).text('Result: ' + data['state']);
			}
		}
		else {
			// rerun in 2 seconds
			setTimeout(function() {
				update_progress(status_url, nanobar, status_div);
			}, 2000);
		}
	});
}


function run_index_page(src_data) {
// send ajax POST request to show index page
	$.ajax({
		type: 'POST',
		url: '/',
		data: src_data,
		dataType: "json",
		success: function(response) {
			console.log(response);
		},
		error: function() {
			alert('An unexpected error occurred');
		}
	});
}


function overlay_on() {
	document.getElementById("overlay").style.display = "block";
}


function overlay_off() {
	document.getElementById("overlay").style.display = "none";
}



//*********************************************   2  *********************************************




//*********************************************  3  *********************************************




//*********************************************  4  *********************************************