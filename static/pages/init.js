const id = location.toString().split('/')[4];
const url = "/workspace/get_info";

async function getdata() {
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


(async()=>{
console.log(await getdata())
})()