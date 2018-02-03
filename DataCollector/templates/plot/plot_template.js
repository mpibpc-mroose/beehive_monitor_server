// var time_format = "{{ plot.time_format }}";
var time_format = "MM-DD-YYYY";
var weight_color = "{{ plot.colors.weight }}";
var temperature_color = "{{ plot.colors.temperature }}";
var humidity_color = "{{ plot.colors.humidity }}";
var ctx = document.getElementById("{{ plot.css_id }}").getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
data: {
    labels: {{plot.labels}},
    datasets: [{
        label: "Gewicht",
        fill: false,
        borderColor: weight_color,
        pointRadius: 3,
        backgroundColor: "rgba(0,0,0,0.1)",
        yAxisID: 'weight',
        data: {{ plot.weights }}
    }, {
        label: "Temperatur",
        yAxisID: 'temp',
        fill: false,
        borderColor: temperature_color,
        pointRadius: 3,
        backgroundColor: "rgba(0,0,0,0.1)",
        data: {{ plot.temperatures }}
    }, {
        label: "Luftfeuchte",
        yAxisID: 'humidity',
        fill: false,
        pointRadius: 3,
        borderColor: humidity_color,
        backgroundColor: "rgba(0,0,0,0.1)",
        data: {{ plot.humidities }}
    }]
},
    options: {
        scales: {
            xAxes: [{
                type: "time",
                distribution: 'linear',
                time: {
                    unit: "hour",
                    stepSize: 6,
                    displayFormats: {
                        hour: 'DD.M.YY-HH:mm'
                    }
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Zeit'
                }
            }],
            yAxes: [{
                id: 'weight',
                type: 'linear',
                position: 'left',
                ticks: {
                  fontColor: weight_color,
                  suggestedMin: {{ plot.scales.weight.min }},
                  suggestedMax: {{ plot.scales.weight.max }},
                  stepSize: 1
                }
                }, {
                id: 'temp',
                type: 'linear',
                position: 'right',
                ticks: {
                  fontColor: temperature_color,
                  suggestedMin: {{ plot.scales.temperature.min }},
                  suggestedMax: {{ plot.scales.temperature.max }},
                  stepSize: 2.5
                }
                } , {
                id: 'humidity',
                type: 'linear',
                position: 'right',
                ticks: {
                  fontColor: humidity_color,
                  min: {{ plot.scales.humidity.min }},
                  max: {{ plot.scales.humidity.max }},
                  stepSize: 10
                }
                }]
        }
    }
});