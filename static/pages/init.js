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

async function deleteColumn(id){
    const url_dc = '/delete_column'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id})
    }
    var response_dc = await fetch(url_dc, settings);
    return await response_dc.json()
}

async function editDescription(id, description){
    const url_ed = '/edit_description'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id, description})
    }
    console.log({id, description})
    var response_ed = await fetch(url_ed, settings);
    return await response_ed.json();
}

async function editTask(id, name){
    const url_ed = '/edit_task_name'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id, name})
    }
    var response_ed = await fetch(url_ed, settings);
    return await response_ed.json();
}

async function deleteTask(id){
    const url_ed = '/delete_task'
    const settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id})
    }
    var response_ed = await fetch(url_ed, settings);
    return await response_ed.json();
}

(async()=>{
    var img = '<img class="delete-column" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAABfUlEQVRoge2YoU4DQRCG/7mro+Wuvjg8JCXhHRC8BAmmtRCqQEIguIoqPMEhEPAKfQECDgvljuLIDYYmFO56O+zS5ch8ZsU/sztf9tYcoCiK4hNyuVl/d3gAxv6sGmY+6p6s7bk605mAyfATXEoYCVye3W8gywYAWi4ONeCBQdubW8tXZYWB0XbzHR4AWgQemBSaCcx3+AlLJkWmAn8W0SPu7wz5twb5TOe4bTxX5W9ABXxTeYGaTfNo9II0fUW0uIC42fiWJckYABBH9dy8qFeC1Q0kyRhZluH5Y9CvGTODmQvzol4JVgLMPLXmZWV5Xiah8m9ABXyjAr5RAd+ogG9UwDcq4BsV8I0K+MZKgIim1rysLM/LJFgJxFEdQUCIonpuRkQgKs6LeiVY/ZWIm43CPwqzMpPcFOkNpNYnlpNIimUCjBtR/U9gvpaUiwQ4C3sAHkUDSfYHPaFGPUmPSKB7unobvIUrIJzD7eeUgvmCQl7vHLbvHO6rKP+ed2yBftABMd1OAAAAAElFTkSuQmCC"/>'
    var columnobjects = await getcolumns();
    main = document.getElementById('Todo');
    for (var i = 0; i < Object.keys(columnobjects).length; i++){
        columns.push(parseInt(columnobjects[i]['column_id']))
    }
    for (var i = Object.keys(columnobjects).length - 1; i >= 0; i--){
        main.insertAdjacentHTML('afterbegin', '<div class="list-group" id="' +  columnobjects[i]['column_id'] + '"> <p>' + columnobjects[i]['column_name'] + '</p>' + '<p class="delete-button">???</p>' + '<div class="hidden list-group-item"></div><input class="create-button" placeholder="+ ???????????????? ????????????!"</div>')
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

    wrapper.addEventListener('click', (event) => {
        if(event.target.className == "list-group-item"){
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('task-window').style.display = 'block';
            tid = event.target.id.slice(1)
            for (var i = Object.keys(taskobjects).length - 1; i >= 0; i--){
                //console.log(taskobjects[i]['column_id'])
                //console.log(i, toString(taskobjects[i]['column_id']))
                if (parseInt(tid) == taskobjects[i]['task_id']){
                    var cur_task = taskobjects[i]
                    var cur_task_ind = i
                }
            }
            document.getElementById('task-window').addEventListener('keydown', (event) => {
                if (event.target.getAttribute('class') == 'task-description' && event.key == 'Enter'){
                    var main_id = cur_task['task_id']
                    editDescription(main_id, event.target.value)
                    event.target.blur()
                    cur_task['task_description'] = event.target.value
                    console.log(cur_task['task_description'])
                } else if(event.target.getAttribute('class') == 'task-name' && event.key == 'Enter'){
                    console.log('Fa')
                    var main_id = cur_task['task_id']
                    editTask(main_id, event.target.value)
                    event.target.blur()
                    cur_task['task_name'] = event.target.value

                    document.getElementById("t" + main_id).textContent = event.target.value
                }
            })
            document.getElementById('task-window').addEventListener('click', (event) => {
                if(event.target.className == 'del_task_btn'){
                    currr_id = event.target.parentElement.parentElement.className.slice(2)
                    deleteTask(currr_id)
                    document.getElementById('task-window').innerHTML=""
                    document.getElementById('overlay').style.display = 'none';
                    document.getElementById('task-window').style.display = 'none';
                    document.body.style.overflow = 'visible';
                    
                    document.getElementById('t' + String(currr_id)).remove()

                }
            })
            console.log(cur_task['task_description'])
            document.getElementById('task-window').setAttribute('class', 'tw' + cur_task['task_id'])
            document.getElementById('task-window').insertAdjacentHTML('afterbegin', '<input class="task-name" value="' + cur_task['task_name'] + '"><div class="description-wrapper"><p class="desc-name">????????????????:</p><textarea placeholder="???????????????? ????????????????..." class="task-description">' + cur_task['task_description'] + '</textarea><p class="del_task_btn">??????????????</p></div>')
        }
    })
    document.getElementById('overlay').addEventListener('click', (event) => {
        document.getElementById('task-window').innerHTML=""
    })
})()
