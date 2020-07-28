import React, { useState, useEffect } from "react"

export function VisParams(props) {

    let controls = ""
    if (props.chartType === "Circular Hierarchical - Single Hue") {
        controls = (
            <div style={{display: "grid", paddingLeft: 20, gridTemplateColumns: "60px 150px 50px"}}>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:2, gridColumn:1}}>Support</p>
                <input style={{ float: "left", marginTop: -25, gridRow:2, gridColumn:2}} type="range" min="1" max="20" defaultValue={props.support} id="support" onChange={(e)=> props.handleSupport(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:2, gridColumn:3}}>{props.support}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:3, gridColumn:1}}>Beta</p>
                <input style={{ float: "left", marginTop: -25, gridRow:3, gridColumn:2}} type="range" min="0" max="1" step="0.1" defaultValue={props.beta} id="support" onChange={(e)=> props.handleBeta(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:3, gridColumn:3}}>{props.beta}</p>
            </div>
        )
    }
    if (props.chartType === "Circular Hierarchical") {
        controls = (
            <div style={{display: "grid", paddingLeft: 20, gridTemplateColumns: "60px 150px 50px"}}>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:1, gridColumn:1}}>Focus</p>
                <input style={{ float: "left", marginTop: -25, gridRow:1, gridColumn:2}} type="range" min="0.1" max="5" step="0.1" defaultValue={props.focus} id="focus" onChange={(e)=> props.handleFocus(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:1, gridColumn:3}}>{props.focus}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:2, gridColumn:1}}>Support</p>
                <input style={{ float: "left", marginTop: -25, gridRow:2, gridColumn:2}} type="range" min="1" max="20" defaultValue={props.support} id="support" onChange={(e)=> props.handleSupport(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:2, gridColumn:3}}>{props.support}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:3, gridColumn:1}}>Beta</p>
                <input style={{ float: "left", marginTop: -25, gridRow:3, gridColumn:2}} type="range" min="0" max="1" step="0.1" defaultValue={props.beta} id="support" onChange={(e)=> props.handleBeta(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:3, gridColumn:3}}>{props.beta}</p>
            </div>
        )
        console.log(controls)
    }
    else {
        controls = (
            <div style={{display: "grid", paddingLeft: 20, gridTemplateColumns: "60px 150px 50px"}}>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:1, gridColumn:1}}>Focus</p>
                <input style={{ float: "left", marginTop: -25, gridRow:1, gridColumn:2}} type="range" min="0.1" max="5" step="0.1" defaultValue={props.focus} id="focus" onChange={(e)=> props.handleFocus(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:1, gridColumn:3}}>{props.focus}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:2, gridColumn:1}}>Support</p>
                <input style={{ float: "left", marginTop: -25, gridRow:2, gridColumn:2}} type="range" min="1" max="20" defaultValue={props.support} id="support" onChange={(e)=> props.handleSupport(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:2, gridColumn:3}}>{props.support}</p>
            </div>
        )
    }

    return (
        <div>
        {controls}
        </div>
    )
}