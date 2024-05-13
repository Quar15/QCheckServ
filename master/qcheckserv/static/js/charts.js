var ctxCpu = document.getElementById("cpuChart").getContext("2d");
var ctxLoadAvg = document.getElementById("loadAvgChart").getContext("2d");
var ctxMemory = document.getElementById("memoryChart").getContext("2d");
var ctxStorage = document.getElementById("storageChart").getContext("2d");
var ctxNetwork = document.getElementById("networkChart").getContext("2d");

// @TODO: This will break if the mountpoints changed
var mountpointData = [];
valuesPartitions[valuesPartitions.length-1].forEach((mountpoint) => {
    mountpointData.push({label: mountpoint["mountpoint"], data: [], graph_data: []});
});
console.log(valuesPartitions[0]);
console.log(mountpointData);
for (let i = 0; i < valuesPartitions.length; i++) {
    for (let j = 0; j < valuesPartitions[i].length; j++) {
        mountpointData[j]["data"].push({
            "usage_perc": valuesPartitions[i][j]["usage_perc"],
            "total": valuesPartitions[i][j]["total"] / 1024 / 1024 / 1024,
            "used": valuesPartitions[i][j]["used"] / 1024 / 1024 / 1024,
            "left": (valuesPartitions[i][j]["total"] - valuesPartitions[i][j]["used"]) / 1024 / 1024 / 1024
        });
        mountpointData[j]["graph_data"].push(valuesPartitions[i][j]["usage_perc"]);
    }
}

var storageListTable = document.querySelector("#storage-list-table");
mountpointData.forEach((mountpoint) => {
    let tr = document.createElement("tr");
    
    let mountpointTd = document.createElement("td");
    mountpointTd.innerText = mountpoint["label"];
    tr.appendChild(mountpointTd);

    if (mountpoint["data"][mountpoint["data"].length - 1]["usage_perc"] != 'ERROR') {
        let usedTd = document.createElement("td");
        usedTd.innerText = padNum(mountpoint["data"][mountpoint["data"].length - 1]["usage_perc"].toFixed(2), 5) + '%';
        tr.appendChild(usedTd);
    
        let usedGbTd = document.createElement("td");
        usedGbTd.innerText = mountpoint["data"][mountpoint["data"].length - 1]["used"].toFixed(2) + ' GB';
        tr.appendChild(usedGbTd);
    
        let leftGbTd = document.createElement("td");
        leftGbTd.innerText = mountpoint["data"][mountpoint["data"].length - 1]["left"].toFixed(2) + ' GB';
        tr.appendChild(leftGbTd);
    
        let totalGbTd = document.createElement("td");
        totalGbTd.innerText = mountpoint["data"][mountpoint["data"].length - 1]["total"].toFixed(2) + ' GB';
        tr.appendChild(totalGbTd);
    }

    storageListTable.appendChild(tr);
});

var configCpu = createConfig('CPU Usage', labels, valuesCpu, '%');
var configLoadAvg = createConfig('1 minute', labels, valuesOneMinuteLoadAvg, '');
var configMemory = createConfig('Memory Usage', labels, valuesMem, '%');
var configStorage = createConfig('ROOT', labels, mountpointData.shift()["graph_data"], '%');
var configNetwork = createConfig('Download', labels, valuesBytesReceived, 'MB/s');

var lineChartCpu = new Chart(ctxCpu, configCpu);
var lineChartLoadAvg = new Chart(ctxLoadAvg, configLoadAvg);
var lineChartMemory = new Chart(ctxMemory, configMemory);
var lineChartStorage = new Chart(ctxStorage, configStorage);
var lineChartNetwork = new Chart(ctxNetwork, configNetwork);

addDataset(lineChartNetwork, {
    label: "Upload",
    backgroundColor: 'rgba(132, 99, 255, 0.2)',
    borderColor: 'rgba(132, 99, 255, 1)',
    fill: true,
    borderWidth: 3,
    data: valuesBytesSent,
});

addDataset(lineChartLoadAvg, {
    label: "5 minutes",
    backgroundColor: 'rgba(132, 99, 255, 0.2)',
    borderColor: 'rgba(132, 99, 255, 1)',
    fill: true,
    borderWidth: 3,
    data: valuesFiveMinuteLoadAvg,
});

addDataset(lineChartLoadAvg, {
    label: "10 minutes",
    backgroundColor: 'rgba(255, 132, 99, 0.2)',
    borderColor: 'rgba(255, 132, 99, 1)',
    fill: true,
    borderWidth: 3,
    data: valuesFifteenMinuteLoadAvg,
});

for (let i = 0; i < mountpointData.length; i++) {
    addDataset(lineChartStorage, {
        label: mountpointData[i]["label"],
        backgroundColor: 'rgba(' + COLORS[i+1] + ', 0.2)',
        borderColor: 'rgba(' + COLORS[i+1] + ', 1)',
        fill: true,
        borderWidth: 3,
        data: mountpointData[i]["graph_data"],
    });
};

var charts = [lineChartCpu, lineChartLoadAvg, lineChartMemory, lineChartStorage, lineChartNetwork];
charts.forEach((chart) => {
    addLineToChart(chart, 'transparent', 0);
});
addLineToChart(lineChartCpu, 'transparent', 25);
addLineToChart(lineChartMemory, 'transparent', 25);
addLineToChart(lineChartStorage, 'transparent', 25);


updateFilterList();