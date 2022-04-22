console.log("Script Active")
const params = {group: 'shared', draggable:'.list-group-item', ghostClass:"ghost", dragClass:"drag", chosenClass: "choose", forceFallback:true}
var elements = document.getElementsByClassName('list-group')

Array.from(elements).forEach(element => {
    Sortable.create(element, params);
});

document.getElementById('hero-btn').addEventListener('click', function(){
    document.getElementById('scrollTo').scrollIntoView({block: 'end', behavior: 'smooth'})
})