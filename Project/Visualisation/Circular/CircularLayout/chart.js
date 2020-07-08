document.addEventListener("DOMContentLoaded", function (event) {
    creatChart = (thresh) => {
        fetch("http://localhost:5000/circular/" + thresh).then(r => r.json()).then(data => {

            const order = data.order
            const sets = data.sets

            const width = 800
            const height = 800
            const r = 350

            const focus = 200

            // Calculate radial coordinate from ordered list of nodes
            const sc_radial = d3.scalePoint().domain(order).range([0, Math.PI * 2])

            // Convert radial coordinate to cartesian
            node2point = (d) => {
                return { x: r * Math.sin(sc_radial(d)), y: r * Math.cos(sc_radial(d)) }
            }

            // Remove existing chart ready for update
            d3.select("#chart")
                .selectAll("*")
                .remove()

            // Append svg element to chart area
            const svg = d3.select("#chart")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .style("display", "block")
                .style("margin", "auto")


            // Centre of the circle
            const centre = { x: width / 2, y: width / 2 }

            // Create objects containing node labels and coordinates from list of edges (sets)
            const node_points = order.map(x => ({ "label": x, "coords": node2point(x) }))

            // Append node groups
            const nodes_group = svg.selectAll("g")
                .data(node_points.slice(0, -1))
                .enter()
                .append("g")
                .attr("transform", (d) => {
                    var x = centre.x + d.coords.x
                    var y = centre.y - d.coords.y
                    return "translate(" + x + "," + y + ")"
                })

            // Append node circles to node groups
            const nodes = nodes_group.append("circle")
                .attr("class", "node")
                .attr("r", 5)

            // Text offset
            const labelOffset = 0.06

            // Append text to labels
            const labels = nodes_group.append("text")
                .text((d) => d.label)
                .attr("fill", "black")
                .attr("dx", (d) => d.coords.x * labelOffset)
                .attr("dy", (d) => -d.coords.y * labelOffset)
                .attr("text-anchor", "middle")
                .attr("font-size", 10)


            const beta = 0
            const lineGen = d3.line().x(d => d.x + centre.x).y(d => centre.y - d.y).curve(d3.curveBundle.beta(beta / 1000))

            // inner point for edge bundling
            const path_factor = 1.2

            const links = svg.selectAll("path")
                .data(sets)
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", (d) => lineGen([node2point(d.labels[0]),
                {
                    x: node2point(d.labels[0]).x / path_factor,
                    y: node2point(d.labels[0]).y / path_factor
                },
                {
                    x: node2point(d.labels[1]).x / path_factor,
                    y: node2point(d.labels[1]).y / path_factor
                },
                node2point(d.labels[1])]))
                .attr("stroke", "black")
                .attr("fill", "none")
                .attr("stroke-width", 1)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** (focus / 100))

            nodes_group.on("mouseenter", (sel) => {
                d3.selectAll(".link")
                    .filter(d => d.labels.includes(sel.label))
                    .raise()
                    .transition(0.1)
                    .attr("stroke", "red")
                    .attr("stroke-width", 3)
                    .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** 1.5)
            })

            nodes_group.on("mouseleave", (sel) => {
                d3.selectAll(".link")
                    .filter(d => d.labels.includes(sel.label))
                    .transition(0.1)
                    .attr("stroke", "black")
                    .attr("stroke-width", 1)
                    .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** (focus / 100))
            })
        })
    }

    let slider = document.getElementById("supportThreshold")
    creatChart(slider.value)


    slider.onchange = () => {
        creatChart(slider.value)
    }


});