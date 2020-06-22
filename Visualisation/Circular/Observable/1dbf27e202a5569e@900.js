// https://observablehq.com/d/1dbf27e202a5569e@900
export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], function(md){return(
md`# Chords circular frequent itemsets - local server`
)});
  main.variable(observer("viewof beta")).define("viewof beta", ["html"], function(html){return(
html`<input type="range" min="0" max="1000" value="0"></input>`
)});
  main.variable(observer("beta")).define("beta", ["Generators", "viewof beta"], (G, _) => G.input(_));
  main.variable(observer("viewof focus")).define("viewof focus", ["html"], function(html){return(
html`<input type="range" min="0" max="1000" value="200"></input>`
)});
  main.variable(observer("focus")).define("focus", ["Generators", "viewof focus"], (G, _) => G.input(_));
  main.variable(observer("chart")).define("chart", ["d3","width","height","node_list","node2point","beta","data","focus"], function(d3,width,height,node_list,node2point,beta,data,focus)
{
  const svg = d3.create("svg")
                .attr("viewBox", [0, 0, width, height]); 
  
  const centre = {x:width/2,y:width/2}
  
  const node_points = node_list.map(x=>({"label":x,"coords":node2point(x)}))
  
  
  const nodes_group = svg.selectAll("g")
                       .data(node_points.slice(0,-1))
                       .enter()
                       .append("g")
                       .attr("transform",(d)=>{
                       var x = centre.x + d.coords.x
                       var y = centre.y - d.coords.y
                       return "translate("+x+","+y+")"  
                       })
  
  const nodes = nodes_group.append("circle")
                   .attr("class","node")
                   .attr("r",5)
 
  
  const labelOffset = 0.05
  
  const labels = nodes_group.append("text")
       .text((d)=>d.label)
       .attr("fill","black")
       .attr("dx",(d)=>d.coords.x*labelOffset)
       .attr("dy",(d)=>-d.coords.y*labelOffset)
       .attr("text-anchor", "middle")
       .attr("font-size",10)
  
  
  const lineGen = d3.line().x(d=>d.x+centre.x).y(d=>centre.y-d.y).curve(d3.curveBundle.beta(beta/1000))
  
  const path_factor = 1.2
  
  const links = svg.selectAll("path")
                   .data(data)
                   .enter()
                   .append("path")
                   .attr("class","link")
                   .attr("d",(d)=>lineGen([node2point(d.labels[0]),
                                           {x:node2point(d.labels[0]).x/path_factor,
                                            y:node2point(d.labels[0]).y/path_factor},
                                           {x:node2point(d.labels[1]).x/path_factor,
                                            y:node2point(d.labels[1]).y/path_factor},
                                           node2point(d.labels[1])]))
                   .attr("stroke","black")
                   .attr("fill","none")
                   .attr("stroke-width",1)
                   .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**(focus/100))
  
  nodes_group.on("mouseenter",(sel)=>{
    d3.selectAll(".link")
      .filter(d=>d.labels.includes(sel.label))
      .raise()
      .transition(0.1)
      .attr("stroke","red")
      .attr("stroke-width",3)
      .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**1.5)
  })
  
  nodes_group.on("mouseleave",(sel)=>{
    d3.selectAll(".link")
      .filter(d=>d.labels.includes(sel.label))
      .transition(0.1)
      .attr("stroke","black")
      .attr("stroke-width",1)
      .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**(focus/100))
  })
 // svg.append("circle").attr("r",r).attr("cy",centre.y).attr("cx",centre.x).attr("stroke","gray").attr("fill","none").attr("stroke-width",0.1)
  
  return svg.node()
}
);
  main.variable(observer("node2point")).define("node2point", ["r","sc_radial"], function(r,sc_radial){return(
(d) => {
 return  {x: r * Math.sin(sc_radial(d)), y: r * Math.cos(sc_radial(d))}
}
)});
  main.variable(observer("sc_radial")).define("sc_radial", ["d3","node_list"], function(d3,node_list){return(
d3.scalePoint().domain(node_list).range([0,Math.PI*2])
)});
  main.variable(observer("width")).define("width", function(){return(
1000
)});
  main.variable(observer("height")).define("height", function(){return(
1000
)});
  main.variable(observer("r")).define("r", function(){return(
400
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@5")
)});
  main.variable(observer("data")).define("data", async function(){return(
(await (await fetch("http://127.0.0.1:5000/circular")).json()).sets
)});
  main.variable(observer("node_list")).define("node_list", async function(){return(
(await (await fetch("http://127.0.0.1:5000/circular")).json()).order
)});
  return main;
}
