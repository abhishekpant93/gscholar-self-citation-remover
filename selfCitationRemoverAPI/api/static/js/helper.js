// var test_local = true;
var test_local = false;
var base_url = '';
if (test_local){
	base_url = 'http://127.0.0.1:8000/'
}else{
	base_url = 'http://social-comp.elasticbeanstalk.com/';
}


var table = null;
$(document).ready(function() {
	$('#fetch_papers').click(fetch_papers);
	$('#ajaxBusy').css({
	    display:"none",
	    margin:"0px",
	    paddingLeft:"0px",
	    paddingRight:"0px",
	    paddingTop:"0px",
	    paddingBottom:"0px",
	    position:"absolute",
	    right:"3px",
	    top:"3px",
	    width:"auto"
	});
});


$(document).ajaxStart(function(){ 
  $('#ajaxBusy').show(); 
}).ajaxStop(function(){ 
  $('#ajaxBusy').hide();
});




function fetch_papers(){
	var author_name = $("#author_name").val();
	if (author_name == ""){
		alert("Author name is not provided !");
		return;
	}
	var data = {};
	data["name"] = author_name;
	var end_point = "getAuthorInfo";
	make_ajax_request_get(base_url,end_point,data,update_paper_list);
	return;
}

function update_paper_list(result){
	// alert(result);
	if(table != null){
		table.destroy();
	}
	if( $('#paper_list_table').length )         // use this if you are using id to check
	{
		// it exists
		$('#paper_list_table').empty();
	}else{
		$('#paper_list').html("<table id=\"paper_list_table\"></table>");
	}
	// parsed_result = JSON.parse(result);
	var parsed_result = result;
	var paper_list = [];
	for (i in parsed_result){
		paper_list.push({"name":parsed_result[i][0],"link":parsed_result[i][1]})
	}
	enable_data_table(paper_list);
	return;
}


/************** general functions *******************/
function make_ajax_request(object_to_pass,url_func,success_function){
	var submit_url = base_url + url_func;
	$.ajax({
		type : "POST",
		url : submit_url,
		data :object_to_pass,
		success : function(result){
			success_function(result);
		},
		error : function() {
			alert("Unable to submit");
		}
	});
}

function make_ajax_request_get(base_url,end_point,data,success_function){
	var url = base_url + end_point;
	$.ajax({
		type : "GET",
		url : url,
		crossDomain: true,
		contentType: "application/json",
		dataType:'json',
		data : data,
		success : function(result){
			success_function(result);
		},
		error : function(data, status, error) {
			console.log("data",data);
			console.log("status",status);
			console.log("error",error);
		}
	});
}
function add_self_citation_analyze_button_info(data,i,j){
	var button_id = "self_analyze_" + i;
	var button = "<button id=\"" + button_id + "\" class=\"btn btn-primary\">Self Analyze</button>";
	
	var name = $("#author_name").val();
	var title = data[i]["title"];
	var url = data[i]["link"];
	
	var param_string = "{name:\"" + name + "\",title:\"" + title + "\",url:\"" + url + "\"}";
	var js_script = "<script>$(\"#" + button_id + "\").click(" + param_string + ",analyze_self_citation);</script>";
	data[i]['Self Citation Info'] = button + js_script;
	return;
}

function analyze_self_citation(passed_data){
	var name = passed_data.data.name;
	var title = passed_data.data.title;
	var url = passed_data.data.url;

	var data = {};
	data["name"] = name;
	data["title"] = title;
	data["url"] = url;
	var end_point = "getSelfCitations";
	make_ajax_request_get(base_url,end_point,data,display_self_citation_info);
}

function display_self_citation_info(result){
	
	var total_citations = result.total_citations;
    var self_citation_papers = result.self_citation_papers;
	var self_citation_info = "Ratio = " + result.ratio + "(" + self_citation_papers + "/" + total_citations + ")";
	

	var paper_list = result.papers;
	var msg_list = [self_citation_info];
	for (i in paper_list){
		var author_msg = "Author List = " + result.papers[0].author;
		var publishing_info = "Pub Info = " + result.papers[0].booktitle;
		var year_info = "Year = " + result.papers[0].year;

		var data = [author_msg,publishing_info,year_info];
		
		var message = "<p>" + data.join("</p><p>") + "</p>";
	
		msg_list.push(message);
	}

	var message ="<p>" +  msg_list.join("</p>------------------<p>") + "</p>";

	

	bootbox.dialog({
		message: message,
	  	title: "Self Citing Papers",
	  	buttons: {
	    	success: {
	      		label: "Success!",
	      		className: "btn-success",
	      		callback: function() {
	        		
	      		}
	    	}
	  	}
	});
}

function get_extra_columns(){
	return ['Self Citation Info'];
}
function add_extra_column_in_data_table_object(data,extra_columns){
	// it is assumed that extra columns will always come in the beginning
	for (var i in data){
		for (var j in extra_columns){
			if (extra_columns[j] == 'Self Citation Info'){
				add_self_citation_analyze_button_info(data,i,j);
			}else{
				// this is the fall back code for handling extra columns
				data[i][extra_columns[j]] = 'test';
			}
		}
	}
	return;
}
function get_column_names(data){
	var column_names = [];
	for (var key in data){
		column_names.push(key);
	}
	return column_names;
}

function enable_data_table(actual_data){
	var data = actual_data;
	if(data.length == 0){
		alert("0 records found !");
		return;
	}
	column_names = get_column_names(data[0]);
	extra_columns = get_extra_columns();
	add_extra_column_in_data_table_object(data,extra_columns);
	total_column_list = extra_columns.concat(column_names);



	// alert(column_names);
	var data_table_columns_object = [];
	

	column_index = new Object();

	for (var i in total_column_list){
		data_table_columns_object.push({data : total_column_list[i],title : total_column_list[i]});
		column_index[total_column_list[i]] = i;
	}

	table = $('#paper_list_table').DataTable( {
	    data: data,
	    dom: 'Bfrtip',
	    columns: data_table_columns_object,
	    buttons: [
	    	'colvis',
            'csvHtml5',
            {
                extend: 'csvHtml5',
                text: 'Export Selected',
                exportOptions: {
                    modifier: {
                        selected: true
                    }
                }
            }
        ],
        select: true
	} );

	// make_columns_visible(table);
	return;
}