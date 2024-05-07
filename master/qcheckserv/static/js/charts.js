function addData(chart, newData, datasetIndex = -1) {
    if (datasetIndex >= 0) {
        chart.data.datasets[datasetIndex].data.push(newData);
    } else {
        chart.data.datasets.forEach((dataset) => {
            dataset.data.push(newData);
        });
    }
    chart.update();
    // removeData(chart);
}

function addDataset(chart, dataset) {
    chart.config.data.datasets.push(dataset);
    chart.update();
}

function removeData(chart) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    chart.update();
}

function createConfig(labelText, dataLabels, dataValues, yAxisUnit = '%') {
    return {
        type: "line",
        data: {
            labels: dataLabels,
            datasets: [
                {
                    label: labelText,
                    data: dataValues,
                    fill: true,
                    backgroundColor: BACKGROUND_COLOR,
                    borderColor: BORDER_COLOR,
                    lineTension: 0.01
                }
            ]
        },
        options: {
            hover: {
                intersect: false,
            },
            interaction: {
                intersect: false,
                mode: 'nearest',
                axis: 'x'
            },
            indexAxis: "x",
            responsive: false, // Use specified width and height
            scales: {
                y: {
                    ticks: {
                        callback: function(value, index, values) {
                            return value + ' ' + yAxisUnit;
                        }
                    },
                    grid: {
                        color: GRID_COLOR,
                    },
                    border: {
                        display: false,
                        dash: [5, 5],
                    },
                },
                x: {
                    grid: {
                        display: false,
                        lineWidth: 0,
                    },
                    type: 'time',
                    time: {
                        unit: "minute",
                        displayFormats: {
                            minute: 'yyyy-MM-dd HH:mm'
                        }
                    },
                    offsetAfterAutoskip: true,
                    min: '2020-01-01 08:00:00',
                    max: '2020-01-01 09:00:00',
                    ticks: {
                        source: 'labels',
                        minRotation: 45
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: "interpolate",
                    intersect: false,
                    animation: false,
                },
                crosshair: {
                    line: {
                        color: CROSSHAIR_COLOR,
                    },
                    snap: {
                        enabled: true
                    },
                    sync: {
                        enabled: true,
                        group: 1,
                        suppressTooltips: false,
                    },
                    zoom: {
                        enabled: false
                    }
                },
            },
        },
    };
}

const BACKGROUND_COLOR = "rgba(99, 255, 132, 0.2)";
const BORDER_COLOR = "rgb(99, 255, 132)";
const CROSSHAIR_COLOR = "rgb(99, 255, 132)";
const GRID_COLOR = "rgba(99, 255, 132, 0.1)";

var ctxCpu = document.getElementById("cpuChart").getContext("2d");
var ctxLoadAvg = document.getElementById("loadAvgChart").getContext("2d");
var ctxMemory = document.getElementById("memoryChart").getContext("2d");
var ctxStorage = document.getElementById("storageChart").getContext("2d");
var ctxNetwork = document.getElementById("networkChart").getContext("2d");


const configCpu = createConfig('CPU Usage', labels, [], '%');
const configLoadAvg = createConfig('1 minute', labels, [], '');
const configMemory = createConfig('Memory Usage', labels, [], '%');
const configStorage = createConfig('ROOT', labels, [], '%');
const configNetwork = createConfig('Download', labels, [], 'MB/s');

var lineChartCpu = new Chart(ctxCpu, configCpu);
var lineChartLoadAvg = new Chart(ctxLoadAvg, configLoadAvg);
var lineChartMemory = new Chart(ctxMemory, configMemory);
var lineChartStorage = new Chart(ctxStorage, configStorage);
var lineChartNetwork = new Chart(ctxNetwork, configNetwork);


// setTimeout(()=>{addData(lineChartLoadAvg, "2020-01-01 09:00:00", 50);}, 2000);
// setTimeout(()=>{addData(lineChartLoadAvg, "2020-01-01 09:05:00", 30);}, 3000);
// setTimeout(()=>{addData(lineChartStorage, "2020-01-01 09:10:00", 69);}, 4000);
// setTimeout(()=>{addData(lineChartStorage, "2020-01-01 09:15:00", 16);}, 5000);

addDataset(lineChartNetwork, {
    label: "Upload",
    backgroundColor: 'rgba(132, 99, 255, 0.2)',
    borderColor: 'rgba(132, 99, 255, 1)',
    fill: true,
    borderWidth: 3,
    data: [],
});

addDataset(lineChartLoadAvg, {
    label: "5 minutes",
    backgroundColor: 'rgba(132, 99, 255, 0.2)',
    borderColor: 'rgba(132, 99, 255, 1)',
    fill: true,
    borderWidth: 3,
    data: [],
});

addDataset(lineChartLoadAvg, {
    label: "10 minutes",
    backgroundColor: 'rgba(255, 132, 99, 0.2)',
    borderColor: 'rgba(255, 132, 99, 1)',
    fill: true,
    borderWidth: 3,
    data: [],
});

valuesCpu.forEach(value => {
    addData(lineChartCpu, value);
    addData(lineChartLoadAvg, value, 0);
    addData(lineChartLoadAvg, value + 5, 1);
    addData(lineChartLoadAvg, value/2, 2);
    addData(lineChartMemory, value);
    addData(lineChartStorage, value);
    addData(lineChartNetwork, value, 1);
    addData(lineChartNetwork, value/2, 0);
});

// Add alert line
lineChartCpu.config.options.plugins.annotation = {
    annotations: [{
        type: 'line',
        mode: 'horizontal',
        scaleID: 'y',
        value: 20,
        borderColor: 'rgb(192, 75, 75)',
        borderWidth: 2,
    }]
};

lineChartCpu.update();