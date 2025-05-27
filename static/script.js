
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
        if (isDebug(e)) {
            const debugCapacity = document.getElementById("debugCapacity")
            if (form.debugCapacity.value === "" || form.debugCapacity.value <= 0) {
                debugCapacity.required = true
                checker.textContent = "debugCapacity required with debug.vrp!!!"
                checker.classList.add("invalid")
                checker.classList.remove("valid")
            } else {
                form.appendChild(retHidden(true))
                form.submit()
            }
        } else {
            form.debugCapacity.value = -1
            form.appendChild(retHidden(false))
            form.submit()
        }
        
    }

})
})
function isDebug(event) {
    X_set = event.target.elements["vrp-file"].value
    if (X_set === "debug") {
        return true
    } else {
        return false
    }
}
function retHidden(value) {
    const hidden = document.createElement("input")
    hidden.type = "hidden"
    hidden.name = "isDebugRun"
    hidden.value = value
    return hidden
}