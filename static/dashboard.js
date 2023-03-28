function chart(labels, data) {
    // Retrieving chart data
    labels = labels.replaceAll("&#39;", "\"")
    labels = Array.from(JSON.parse(labels))

    data = data.replaceAll("&#39;", "\"")
    data = Array.from(JSON.parse(data))

    // Importing colors
    const autocolors = window['chartjs-plugin-autocolors'];
    Chart.register(autocolors);

    stats = document.getElementById("stats")
    // Displaying a bar chart with labels and image counts 
    new Chart(
        stats,
        {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Files",
                        data: data,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                plugins: {
                    autocolors: {
                        mode: 'data'
                    }
                }
            }
        }
    );
}