const id = location.toString().split('/')[4];
const url = "/workspace/get_info";
columns = []


async function getcolumns() {
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id})
    }
    var response = await fetch(url, settings);
    return await response.json();
}

async function get_tasks(id) {
    const url_gc = '/get_tasks'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(id)
    }
    var response = await fetch(url_gc, settings);
    return await response.json();
}

async function newColumn(name, id) {
    const url_nc = '/add_column'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name, id})
    }
    var response_nc = await fetch(url_nc, settings);
    return await response_nc.json()
}

async function newTask(name, column) {
    const url_nc = '/add_task'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name, column})
    }
    var response_nc = await fetch(url_nc, settings);
    return await response_nc.json()
}

async function changeColumn(to, task_id){
    const url_cc = '/change_column'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({to, task_id})
    }
    var response_cc = await fetch(url_cc, settings);
    return await response_cc.json()
}

(async()=>{
    var columnobjects = await getcolumns();
    main = document.getElementById('Todo');
    for (var i = 0; i < Object.keys(columnobjects).length; i++){
        columns.push(parseInt(columnobjects[i]['column_id']))
    }
    for (var i = Object.keys(columnobjects).length - 1; i >= 0; i--){
        main.insertAdjacentHTML('afterbegin', '<div class="list-group" id="' +  columnobjects[i]['column_id'] + '"> <p>' + columnobjects[i]['column_name'] + '</p><div class="hidden list-group-item"></div><input class="create-button" placeholder="+ Создайте задачу!"</div>')
        Sortable.create(main.firstElementChild, params);
        cur_column = main.firstElementChild;
    }
    taskobjects = await get_tasks(columns)
    console.log(taskobjects)
    for (var i = Object.keys(taskobjects).length - 1; i >= 0; i--){
        //console.log(taskobjects[i]['column_id'])
        //console.log(i, toString(taskobjects[i]['column_id']))
        document.getElementById(String(taskobjects[i]['column_id'])).firstElementChild.nextElementSibling.insertAdjacentHTML('afterend', '<div class="list-group-item"' + 'id="t' + taskobjects[i]['task_id'] + '">' + taskobjects[i]['task_name'] + '</div>')
    }
})()
