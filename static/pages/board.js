var moving = false
const params = {group: 'shared', draggable:'.list-group-item', ghostClass:"ghost", dragClass:"drag", chosenClass: "choose", forceFallback:true, onStart: function(evt){
    evt.item.setAttribute('class', 'list-group-item nodrag ghost')
}, onEnd: function(evt){
    if (evt.to != evt.from){
        changeColumn(evt.to.id, evt.item.id.slice(1));
    }
    setTimeout(function(){
        evt.item.setAttribute('class', 'list-group-item');
    }, 1)
}};


console.log("Script Active")

// New element buttons work
var wrapper = document.getElementById('Todo');


wrapper.addEventListener('keydown', (event) => {
    if(event.key == "Enter"){
        console.log(event.target.getAttribute('class'))
        if((event.target.getAttribute('class') == 'create-button') && event.target.value != ""){
            var tname = event.target.value;
            var cid = event.target.parentElement.id;
            var task_id
            async function getTaskId(){
                return await newTask(tname, cid);
            }
            var insert_to = event.target;
            var valueof = event.target.value;
            (async () => {
                task_id = await getTaskId();
                task_id = task_id['id'];
                console.log(task_id);
                insert_to.insertAdjacentHTML('beforebegin', '<div class="list-group-item" id="t' + task_id + '">'+ valueof + "</div>");
            })()

            event.target.value = "";
            event.target.blur();
        } else if (event.target.getAttribute('class') == 'create-column' && event.target.value != ""){
            event.target.parentElement.insertAdjacentHTML('afterEnd','<div class="sort"><input class="create-column" placeholder="Создайте колонну"></div>');
            var element = event.target.parentElement;
            Sortable.create(element, params);
            async function getCurId(){
                var cur_id = await newColumn(event.target.value, id);
                cur_id = cur_id['column_id'];
                console.log(cur_id)
                return cur_id;
            }
            ournewColumn = event.target.parentElement;
            (async () => {
                var cur_id = await getCurId();
                console.log(cur_id)
                ournewColumn.setAttribute('id', cur_id);
            })()
            event.target.parentElement.setAttribute('class', 'list-group')
            event.target.insertAdjacentHTML('beforebegin',"<p>" + event.target.value + '</p><div class="hidden list-group-item"></div><input class="create-button" placeholder=" + Создайте задачу!">');
            event.target.value = "";
            event.target.remove();
        }
    }
})

var buttons = document.getElementsByClassName('create-button')

for(var i = 0; i < buttons.length; i++){
        var cur_button = buttons[i];
        function onBlur(event){
            if((event.target.getAttribute('class') == 'create-button') && event.target.value != ""){
                newTask(event.target.value, event.target.parentElement.id)
                event.target.insertAdjacentHTML('beforebegin', '<div class="list-group-item">' + event.target.value + "</div>");
                event.target.value = "";
                event.target.blur();
            }
        }
        cur_button.addEventListener('blur', onBlur)
}

wrapper.addEventListener('click', (event) => {
    if(event.target.className == "list-group-item"){
        document.getElementById('overlay').style.display = 'block';
        document.getElementById('task-window').style.display = 'block';
    }
})

overlay.addEventListener('click', (event) =>{
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('task-window').style.display = 'none';
    document.body.style.overflow = 'visible';
})
// Task

//async function status_(){
  //  var response = await (await fetch("http://10.206.120.72:1000/status")).json();
    //document.getElementById('status').textContent = response.status;
//}

//status_();

var elements = document.getElementsByClassName('list-group')

Array.from(elements).forEach(element => {
    Sortable.create(element, params);
});
