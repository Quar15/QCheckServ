let headers = document.querySelectorAll(".list-group .item-header");

headers.forEach(header => {
    header.addEventListener("click", () => {
        headers.forEach(e => {
            e.parentElement.classList.remove("active");
            e.querySelector(".icon").innerText = "+";
        });
        header.parentElement.classList.add("active");
        header.querySelector(".icon").innerText = "-";
    })
});

headers[headers.length - 1].click();

let searchBar = document.querySelector("#server-search");
let listGroups = document.querySelectorAll(".list-group");
let tableRecords = document.querySelectorAll(".list-group .item-content td:nth-child(1)");
searchBar.addEventListener("keyup", () => {
    let searchContent = searchBar.value.toLowerCase();
    let re = new RegExp(".*" + searchContent + ".*");
    tableRecords.forEach(e => {
        if (! e.innerText.toLowerCase().match(re)) {
            e.parentElement.classList.add("unfiltered");
        } else {
            e.parentElement.classList.remove("unfiltered");
        }
    });
    listGroups.forEach(group => {
        let tableRows = group.querySelectorAll("tr:has(td)");
        let unfilteredRowsCount = 0;
        tableRows.forEach((r) => {
            if (r.classList.contains("unfiltered")) {
                unfilteredRowsCount++;
            }
        });
        if (unfilteredRowsCount === tableRows.length) {
            group.classList.add("unfiltered");
        } else {
            group.classList.remove("unfiltered");
        }
    });
});