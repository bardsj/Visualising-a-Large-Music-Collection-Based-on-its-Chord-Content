import React from "react";
import * as d3 from 'd3';
import {genreColormap} from './colorMap'

export class ChartParallel extends React.Component {
    constructor(props) {
        super(props)
        this.state = { data: null, request_params: null }
    }

    fetchData(request_params) {
        let r_url = ""
        if (request_params.tag_val.length > 0) {
            r_url = "http://127.0.0.1:5000/parallel?tag_val=" + request_params.tag_val.join() + "&tag_name=" + request_params.tag_name
        }
        else {
            r_url = "http://127.0.0.1:5000/parallel"
        }
        fetch(r_url,{mode: 'cors'})
            .then(r => r.json())
            .then(r => this.setState({ data: r, request_params: request_params },()=>{this.createChart()}))

    }

    componentDidMount() {
        console.log(this.props)
        //this.fetchData(this.props.request_params);
    }

    componentDidUpdate(prevProps) {
        if (prevProps.request_params !== this.props.request_params) {
            this.fetchData(this.props.request_params)
        }
        if (prevProps.support !== this.props.support) {
            this.createChart()
        }
        if (prevProps.focus !== this.props.focus) {
            this.updateFocus()
        }
    }

    createChart() {
        const svg = d3.select(this.refs[this.props.id + 'chartsvg'])
        svg.selectAll("*").remove()
        const width = this.props.width
        const height = this.props.height
        let node_list = this.state.data.order
        let data = this.state.data.sets
        data = data.filter(x=> x.values > this.props.support/100)
        const margin = ({ top: 20, bottom: 20, left: 60, right: 10 })

        // Number of parallel axes from max itemset length
        const n_ax = d3.max(data.map(x => x.labels.length))

        // Filter out nodes from order that all not in filtered sets
        const filtered_set = new Array(... new Set(data.flatMap(x=>x['labels'])))
        node_list = node_list.filter(x=>filtered_set.includes(x))

        // Colour map
        const cmap = genreColormap(this.state.request_params.tag_val)
        // Add axis field for n axes from node list
        let node_list_ax = []

        for (let i = 0; i < n_ax; i++) {
            for (let j = 0; j < node_list.length; j++) {
                node_list_ax.push({ node: node_list[j], ax: i })
            }
        }
        node_list_ax = node_list_ax.flat()

        // Add axes field to data by taking index of node in data node lists
        const data_ax = data.map(d => ({ labels: d.labels.map((l, i) => ({ node: l, ax: i })), values: d.values, tag: d.tag }))

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
            .attr("class", "label")
            .attr("font-size", 10)
            .attr("dx", -4)
            .attr("dy", 2)
            .attr("text-anchor", "end")

        // Add transparent rectangle to labels for easier hover selection
        const label_bg = nodes_group.append("rect")
            .attr("width", 30)
            .attr("height", 20)
            .attr("fill", "transparent")
            .attr("transform", "translate(-34,-6)")

        // Path generator
        const lineGen = d3.line().y(d => scY(d.node)).x(d => scX(d.ax)).curve(d3.curveCardinal)

        // Append paths
        const links = svg.selectAll("path")
            .data(data_ax)
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", d => lineGen(d.labels))
            .attr("fill", "none")
            .attr("stroke", d => {cmap[d.tag]})
            .attr("fill", "none")
            .attr("stroke-width", 1)
            .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** this.props.focus)

        // Highlight paths when hovering on node
        label_bg.on("mouseenter", (sel) => {

            d3.selectAll(".label")
                .filter(l => l == sel)
                .transition(0.1)
                .attr("font-size", 15)


            d3.selectAll(".link")
                //.filter(d=>d.labels.includes(sel.label))
                .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
                .transition(0.1)
                .attr("stroke", "red")
                .attr("stroke-width", 3)
                .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** 1)
        })

        label_bg.on("mouseleave", (sel) => {

            d3.selectAll(".label")
                .filter(l => l == sel)
                .transition(0.1)
                .attr("font-size", 10)

            d3.selectAll(".link")
                .filter(d => d.labels[sel.ax] ? d.labels[sel.ax].node === sel.node : null)
                .transition(0.1)
                .attr("stroke", d => cmap[d.tag])
                .attr("stroke-width", 1)
                .attr("stroke-opacity", d => (d.values / d3.max(data.map(x => x.values))) ** this.props.focus)
        })


        // Raise label groups above paths
        nodes_group.raise()
        label_bg.raise()

        this.setState({sets:data})  
    }

    updateFocus() {
        const svg = d3.select(this.refs[this.props.id + 'chartsvg'])

        svg.selectAll(".link")
            .attr("stroke-opacity", d => (d.values / d3.max(this.state.sets.map(x => x.values))) ** this.props.focus)
    }


    render() {
        return (
            <svg ref={this.props.id + 'chartsvg'} width={this.props.width} height={this.props.height} style={{ display: "block", margin: "auto" }}>

            </svg>
        )
    }

}