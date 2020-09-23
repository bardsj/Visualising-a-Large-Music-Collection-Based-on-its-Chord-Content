import React from "react";
import * as d3 from 'd3';
import { genreColormap } from './colorMap'

export class Legend extends React.Component {
    constructor(props) {
        super(props)
        this.createLegend = this.createLegend.bind(this)
    }

    componentDidMount() {
        this.createLegend()
    }

    componentDidUpdate() {
        this.createLegend()
    }

    createLegend() {
        const svg = d3.select(this.refs["legend"])
        svg.selectAll("*").remove()

        // If single hue chart selected create gradient colour legend else create categorical legend
        if (!this.props.requestParams.chartType.includes("Single Hue")) {
            svg.attr("height", "100%")
            const labels = svg.selectAll("g")
                .data(this.props.requestParams.tag_val)
                .enter()
                .append("g")
                .attr("transform", (d, i) => {
                    return "translate(20," + String((i * 40) + 20) + ")"
                })

            const cmap = genreColormap(this.props.requestParams.tag_val)

            labels.append("rect")
                .attr("fill", d => cmap[d])
                .attr("width", 20)
                .attr("height", 20)

            labels.append("text")
                .text(d => d[0].toUpperCase() + d.slice(1))
                .attr("dx", 25)
                .attr("dy", 15)
                .attr("font-size", 15)

        }
        else {

            const xoffset = 20
            const yoffset = 20
            const height = 200

            const scColor = d3.scaleSequential().domain([0, 100]).interpolator(d3.interpolateYlOrRd)
            const yScale = d3.scaleLinear().domain([0, 100]).range([0, height])
            svg.selectAll("rect")
                .data(d3.range(99))
                .enter()
                .append("rect")
                .attr("width", 20)
                .attr("height", 5)
                .attr("x", 20)
                .attr("y", d => yScale(d) + 20)
                .attr("fill", d => scColor(d))

            svg.append("text")
                .text("Support Value")
                .attr("x", xoffset)
                .attr("y", yoffset + 230)

            svg.append("text")
                .text("0")
                .attr("x", xoffset + 30)
                .attr("y", yoffset + 5)

            svg.append("text")
                .text("0.2")
                .attr("x", xoffset + 30)
                .attr("y", yoffset + height + 5)

            svg.append("line")
                .attr("x1", xoffset)
                .attr("x2", xoffset + 25)
                .attr("y1", yoffset)
                .attr("y2", yoffset)
                .attr("stroke", "black")

            svg.append("line")
                .attr("x1", xoffset)
                .attr("x2", xoffset + 25)
                .attr("y1", yoffset + height)
                .attr("y2", yoffset + height)
                .attr("stroke", "black")

        }
    }

    render() {
        return (<svg ref={"legend"} height="100%"></svg>)
    }
}