function add_param(){
    if(typeof add_param.counter == 'undefined'){
        add_param.counter = 0;
    }
    add_param.counter++;
    id = 'new' + add_param.counter.toString();
    document.getElementById('add_param').innerHTML = document.getElementById('add_param').innerHTML
                + '<input type="button" class="a_button p_button" onclick="clean(' + id + ')"'
                 + 'value="X" title="اضغط لمسح محتوى الإطار">'
                + '<input type="text" id="' + id +'" name="' + id + '" class="input" value="">'
}

function clean(id){ document.getElementById(id).value = '' }

function display_summary(){
    document.getElementById("select_form").action = "/summary";
    document.getElementById("select_form").submit();
}

function delete_summary(){
    document.getElementById("select_form").action = "/delete";
    document.getElementById("select_form").submit();
}

function modify_summary(){
    document.getElementById("select_form").action = "/modify";
    document.getElementById("select_form").submit();
}

function highlight(selected, total) {
    for (var i in total) {
        id = i.toString();
        if (id != selected){
            document.getElementById(id).style.backgroundColor = "#8fe2fd00";
        }else{
            document.getElementById(id).style.backgroundColor = "#8fe2fd80";
        }
    }
}

function display_new_summary(){
    document.getElementById("select_form").action = "new_summary";
    document.getElementById("select_form").submit();
}

function delete_new_summary(){
    document.getElementById("select_form").action = "delete_new";
    document.getElementById("select_form").submit();
}

function get_filename() {
    document.getElementById("select_form").action = "upload";
    document.getElementById("select_form").submit();
}

function summarize(){
    document.getElementById("select_form").action = "summarize";
    document.getElementById("select_form").submit();
}

function save_summaries(){
    document.getElementById("select_form").action = "save_summaries";
    document.getElementById("select_form").submit();
}