// https://observablehq.com/d/9793e388fa64538f@1129
export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], function(md){return(
md`# Chords Parallel (no axis)`
)});
  main.variable(observer("chart")).define("chart", ["d3","width","height","node_list_ax","scX","scY","data_ax","data"], function(d3,width,height,node_list_ax,scX,scY,data_ax,data)
{
  const svg = d3.create("svg")
                .attr("viewBox", [0, 0, width, height]); 
  
   const nodes_group = svg.selectAll("g")
         .data(node_list_ax)
         .enter()
         .append("g")
         .attr("transform",(d)=>"translate("+scX(d.ax)+","+scY(d.node)+")")
   
   const nodes = nodes_group.append("circle")
        .attr("r",2)
  
  const labels = nodes_group.append("text")
       .text(d=>d.node)
       .attr("font-size",8)
       .attr("dx",-4)
       .attr("dy",2)
       .attr("text-anchor", "end")
  
  const lineGen = d3.line().y(d=>scY(d.node)).x(d=>scX(d.ax))
  
  const links = svg.selectAll("path")
     .data(data_ax)
     .enter()
     .append("path")
     .attr("class","link")
     .attr("d",d=>lineGen(d.labels))
     .attr("fill","none")
     .attr("stroke","black")
     .attr("fill","none")
     .attr("stroke-width",1)
     .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**3)
  
    nodes_group.on("mouseenter",(sel)=>{
      d3.select(this).raise()
    d3.selectAll(".link")
      //.filter(d=>d.labels.includes(sel.label))
      .filter(d=>d.labels[sel.ax] ? d.labels[sel.ax].node===sel.node : null)
      .raise()
      .transition(0.1)
      .attr("stroke","red")
      .attr("stroke-width",3)
      .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**1.5)
  })
  
  nodes_group.on("mouseleave",(sel)=>{
    d3.selectAll(".link")
      .filter(d=>d.labels[sel.ax] ? d.labels[sel.ax].node===sel.node : null)
      .transition(0.1)
      .attr("stroke","black")
      .attr("stroke-width",1)
      .attr("stroke-opacity",d=>(d.values/d3.max(data.map(x=>x.values)))**3)
  })
  
  return svg.node()
}
);
  main.variable(observer("scX")).define("scX", ["d3","n_ax","width"], function(d3,n_ax,width){return(
d3.scaleLinear().domain([0,n_ax-1]).range([40,width-10])
)});
  main.variable(observer("scY")).define("scY", ["d3","node_list","height"], function(d3,node_list,height){return(
d3.scalePoint().domain(node_list).range([20,height-20])
)});
  main.variable(observer("n_ax")).define("n_ax", ["d3","data"], function(d3,data){return(
d3.max(data.map(x=>x.labels.length))
)});
  main.variable(observer("width")).define("width", function(){return(
1000
)});
  main.variable(observer("height")).define("height", function(){return(
600
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@5")
)});
  main.variable(observer("data")).define("data", async function(){return(
(await (await fetch("http://127.0.0.1:5000/parallel")).json()).sets
)});
  main.variable(observer("node_list")).define("node_list", async function(){return(
(await (await fetch("http://127.0.0.1:5000/parallel")).json()).order
)});
  main.variable(observer("node_list_ax")).define("node_list_ax", ["n_ax","node_list"], function(n_ax,node_list)
{
   let node_list_ax = []
  
  for(let i = 0; i < n_ax; i++) {
    for(let j = 0;j < node_list.length;j++){
      node_list_ax.push({node:node_list[j],ax:i})
    }
}
  return node_list_ax.flat()
}
);
  main.variable(observer("data_ax")).define("data_ax", ["data"], function(data){return(
data.map(d=>({labels:d.labels.map((l,i)=>({node:l,ax:i})),values:d.values}))
)});
  return main;
}
