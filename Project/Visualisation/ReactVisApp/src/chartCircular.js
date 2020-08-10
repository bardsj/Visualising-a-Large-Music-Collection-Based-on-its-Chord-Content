import React from "react";
import * as d3 from 'd3';
import {genreColormap,nodeColormap} from './colorMap'
import { zip } from "d3";

export class ChartCircular extends React.Component {
    constructor(props) {
        super(props)
        this.state = { data: null, request_params: null }
    }

    fetchData(request_params,optType) {
        let r_url = ""
        if (request_params.tag_val.length > 0) {
            r_url = "http://127.0.0.1:5000/circular?tag_val=" + request_params.tag_val.join() + "&tag_name=" + request_params.tag_name
        }
        else {
            r_url = "http://127.0.0.1:5000/circular?"
        }
        if (optType) {
            r_url = r_url + "&order_opt=" + optType
        }
        fetch(r_url,{mode: 'cors'})
            .then(r => r.json())
            .then(r => this.setState({ data: r, request_params: request_params },()=>{this.createChart()}))

    }

    componentDidMount() {
        this.fetchData(this.props.request_params,this.props.optType)
    }

    componentDidUpdate(prevProps) {
        if (prevProps.request_params !== this.props.request_params) {
            this.fetchData(this.props.request_params,this.props.optType)
        }
        if (prevProps.support !== this.props.support) {
            this.createChart()
        }
        if (prevProps.focus !== this.props.focus) {
            this.updateFocus()
        }
        if (prevProps.optType !== this.props.optType) {
            this.fetchData(this.props.request_params,this.props.optType)
        }
    }


    createChart() {
        const svg = d3.select(this.refs[this.props.id + 'chartsvg'])
        svg.selectAll("*").remove()
        const width = this.props.width
        const height = this.props.height
        let order = this.state.data.order
        let sets = this.state.data.sets
        // Filter based on slider support val
        sets = sets.filter(x=> x.values > this.props.support/100)
        const r = (this.props.height / 2) - 50;

        // Filter out nodes from order that all not in filtered sets
        const filtered_set = new Array(... new Set(sets.flatMap(x=>x['labels'])))
        order = order.filter(x=>filtered_set.includes(x) || x.includes("sep"))

        // Calculate radial coordinate from ordered list of nodes
        const sc_radial = d3.scalePoint().domain(order).range([0, Math.PI * 2 - (Math.PI*2/order.length)])

        // Colour map
        const cmap = genreColormap(this.state.request_params.tag_val)
        const ncmap = nodeColormap()

        // Convert radial coordinate to cartesian
        const node2point = (d) => {
            return { x: r * Math.sin(sc_radial(d)), y: r * Math.cos(sc_radial(d)) }
        }

        // Centre of the circle
        const centre = { x: width / 2, y: width / 2 }

        // Create objects containing node labels and coordinates from list of edges (sets)
        const node_points = order.map(x => ({ "label": x, "coords": node2point(x) }))

        // Append node groups
        const nodes_group = svg.selectAll("g")
            .data(node_points)
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
            .attr("fill",(d)=>{
                if (d.label[1]=="b") {
                    return ncmap[d.label.slice(0,2)]
                }
                else {
                    return ncmap[d.label[0]]
                }
            })

        // Text offset
        const labelOffset = 0.06


        // Append text to labels
        const labels = nodes_group.append("text")
            .text((d) => d.label)
            .attr("fill","black")
            .attr("dx", (d) => d.coords.x * labelOffset)
            .attr("dy", (d) => -d.coords.y * labelOffset)
            .attr("text-anchor", "middle")
            .attr("font-size", 10)


        const beta = 0
        const lineGen = d3.line().x(d => d.x + centre.x).y(d => centre.y - d.y).curve(d3.curveBundle.beta(beta / 1000))

        const links = svg.selectAll("path")
            .data(sets)
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", (d) => lineGen([node2point(d.labels[0]),node2point(d.labels[1])]))
            .attr("stroke", d => cmap[d.tag])
            .attr("fill", "none")
            .attr("stroke-width", 1)
            .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.focus)

        nodes_group.on("mouseenter", (sel) => {
            d3.selectAll(".link")
                .filter(d => d.labels.includes(sel.label))
                .raise()
                .transition(0.1)
                .attr("stroke", "red")
                .attr("stroke-width", 3)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** 1)
                nodes_group.raise()
        })

        nodes_group.on("mouseleave", (sel) => {
            d3.selectAll(".link")
                .filter(d => d.labels.includes(sel.label))
                .transition(0.1)
                .attr("stroke", d => cmap[d.tag])
                .attr("stroke-width", 1)
                .attr("stroke-opacity", d => (d.values / d3.max(sets.map(x => x.values))) ** this.props.focus)
                nodes_group.raise()
        })

        // Remove spacing nodes
        if (!this.props.optType) {
            nodes_group.filter(x=>x.label.includes("sep")).remove()
        }

        // Remove seps from order before writing to state
        order = order.filter(x=>!x.includes("sep"))

        nodes_group.raise()
        this.setState({sets:sets})  
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