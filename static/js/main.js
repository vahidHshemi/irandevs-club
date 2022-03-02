//GET SEARCH FORM AND PAGE LINKS
let searchForm = document.getElementById('searchForm')
let pageLinks = document.getElementsByClassName('page-link')

//ENSURE SEARCH FORM EXISTS
if (searchForm) {
    for (let i = 0; pageLinks.length > i; i++) {
        pageLinks[i].addEventListener('click', function (e) {
            e.preventDefault()

            //GET THE DATA ATTRIBUTE
            let page = this.dataset.page

            //ADD HIDDEN SEARCH INPUT TO FORM
            searchForm.innerHTML += `<input value=${page} name="page" hidden/>`


            //SUBMIT FORM
            searchForm.submit()
        })
    }
}


let tags = document.getElementsByClassName('project-tag')

for (let i = 0; tags.length > i; i++) {
    tags[i].addEventListener('click', (e) => {
        let tagId = e.target.dataset.tag
        let projectId = e.target.dataset.project

        // console.log('TAG ID:', tagId)
        // console.log('PROJECT ID:', projectId)

        fetch('http://127.0.0.1:8000/api/remove-tag/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            // A common use of JSON is to exchange data to/from a web server.
            // When sending data to a web server, the data has to be a string.
            // Convert a JavaScript object into a string with JSON.stringify().
            body: JSON.stringify({'project': projectId, 'tag': tagId})
        })
            // The json() method of the Response interface takes a Response stream and reads it to completion.
            // It returns a promise which resolves with the result of parsing the body text as JSON.
            .then(response => response.json())
            .then(data => {
                e.target.remove()
            })

    })
}
