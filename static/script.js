
document.addEventListener("DOMContentLoaded", ()=> {
document.getElementById("input-form").addEventListener("submit", (e)=>{
    e.preventDefault()

    const form = e.target
    const numThreads = Number(form.numThreads.value)
    const numRealDM = Number(form.numRealDM.value)
    const checker = document.getElementById("input-Checker")
    

    if (numThreads<numRealDM){
        checker.textContent = "numRealDM has to be smaller/= to numThreads"
        checker.classList.add("invalid")
        checker.classList.remove("valid")
    } else {
        checker.textContent = "Valid"
        checker.classList.remove("invalid")
        checker.classList.add("valid")
        form.submit()
    }

})
})