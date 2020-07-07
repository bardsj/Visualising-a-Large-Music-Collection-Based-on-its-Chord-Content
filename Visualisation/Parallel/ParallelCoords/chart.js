document.addEventListener("DOMContentLoaded", function (event) {
    creatChart = (thresh) => {
        fetch("http://localhost:5000/parallel/" + thresh).then(r => r.json()).then(d => {

            const node_list = d.order
            const data = d.sets

            const width = 1400
            const height = 800

            const margin = ({top:20,bottom:20,left:60,right:10})

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

            // Number of parallel axes from max itemset length
            const n_ax = d3.max(data.map(x => x.labels.length))

            // Add axis field for n axes from node list
            let node_list_ax = []

            for (let i = 0; i < n_ax; i++) {
                for (let j = 0; j < node_list.length; j++) {
                    node_list_ax.push({ node: node_list[j], ax: i })
                }
            }
            node_list_ax = node_list_ax.flat()

            // Add axes field to data by taking index of node in data node lists
            const data_ax = data.map(d => ({ labels: d.labels.map((l, i) => ({ node: l, ax: i })), values: d.values }))

            // Categorical y scale
            const scY = d3.scalePoint().domain(node_list).range([margin.top, height - margin.bottom])
            // Linear x scale for parallel axes
            const scX = d3.scaleLinear().domain([0, n_ax - 1]).range([margin.left, width - margin.right])

            // Add node groups to create parallel axes
            const nodes_group = svg.selectAll("g")
                .data(node_list_ax)
                .enter()
                .append("g")
                .attr("transform", (d) => "translate(" + scX(d.ax) + "," + scY(d.node) + ")")
            // Append circle to node groups
            const nodes = nodes_group.append("circle")
                .attr("r", 2)
            // Append labels to node groups
            const labels = nodes_group.append("text")
                .text(d => d.node)
                .attr("class","label")
                .attr("font-size", 10)
                .attr("dx", -4)
                .attr("dy", 2)
                .attr("text-anchor", "end")

            // Add transparent rectangle to labels for easier hover selection
            const label_bg = nodes_group.append("rect")
                                        .attr("width",30)
                                        .attr("height",20)
                                        .attr("fill","transparent")
                                        .attr("transform","translate(-34,-6)")

            // Path generator
            const lineGen = d3.line().y(d => scY(d.node)).x(d => scX(d.ax))

            // Append paths
            const links = svg.selectAll("path")
                .data(data_ax)
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", d => lineGen(d.labels))
                .attr("fill", "none")
                .attr("stroke", "grey")
                .attr("fill", "none")
                .attr("stroke-width", 1)
                .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 2.5)

            // Highlight paths when hovering on node
            label_bg.on("mouseenter",(sel)=>{
      
                d3.selectAll(".label")
                .filter(l=>l == sel)
                .transition(0.1)
                .attr("font-size",15)
                
                
              d3.selectAll(".link")
                //.filter(d=>d.labels.includes(sel.label))
                .filter(d=>d.labels[sel.ax] ? d.labels[sel.ax].node===sel.node : null)
                .transition(0.1)
                .attr("stroke","red")
                .attr("stroke-width",3)
                .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**1.5)
            })
            
            label_bg.on("mouseleave",(sel)=>{
              
              d3.selectAll(".label")
                .filter(l=>l == sel)
                .transition(0.1)
                .attr("font-size",10)
              
              d3.selectAll(".link")
                .filter(d=>d.labels[sel.ax] ? d.labels[sel.ax].node===sel.node : null)
                .transition(0.1)
                .attr("stroke","grey")
                .attr("stroke-width",1)
                .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**2.5)
            })

            
            // Raise label groups above paths
            nodes_group.raise()
            label_bg.raise()

        })

    }

    let slider = document.getElementById("supportThreshold")
    creatChart(slider.value)
    document.getElementById("sliderValue").innerText = slider.value

    slider.onchange = () => {
        creatChart(slider.value)
        document.getElementById("sliderValue").innerText = slider.value
    }
});