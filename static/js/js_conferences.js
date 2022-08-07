function convertDateToString(date){

}
$('#buttonFormAddConference').click(function() {
    var form = document.getElementById("formAddConference");
    var conf_name = form.elements["name"].value;
    var abstract_submission_deadline = form.elements["abstract_submission_deadline"].value;
    var paper_submission_deadline = form.elements["paper_submission_deadline"].value;
    var review_deadline = form.elements["review_deadline"].value;
    var start_date = form.elements["start_date"].value;
    var end_date = form.elements["end_date"].value;
    var today = new Date();
    var month = today.getMonth() + 1 + "";
    var hour = today.getHours() + "";
    if(month.length == 1){
        month = "0" + month;
    }
    var date = today.getFullYear()+'-'+(month)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes();
    var today = date+'T'+time;
    console.log(today);
    console.log(new Date(Date.parse(abstract_submission_deadline)) > new Date());
    if(conf_name == ""){
        alert("Conference name can't be empty.");
        return false;
    }
    if(end_date.localeCompare(start_date) > 0 && start_date.localeCompare(review_deadline) > 0
    && review_deadline.localeCompare(paper_submission_deadline) > 0 && paper_submission_deadline.localeCompare(abstract_submission_deadline) > 0
    && new Date(Date.parse(abstract_submission_deadline)) > new Date()){

        return true;
    }
    else{
        alert('Check the dates you have entered.');
        return false;
    }
});

