import React, { useState, useEffect } from "react"

export function VisParams(props) {
    return (
        <div style={{display: "grid", paddingLeft: 20, gridTemplateColumns: "60px 150px 50px"}}>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:1, gridColumn:1}}>Focus</p>
                <input style={{ float: "left", marginTop: -25, gridRow:1, gridColumn:2}} type="range" min="0.1" max="3" step="0.1" defaultValue={props.focus} id="focus" onChange={(e)=> props.handleFocus(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:1, gridColumn:3}}>{props.focus}</p>
                <p style={{ float: "left" , paddingRight: 10, paddingBottom: 10, gridRow:2, gridColumn:1}}>Support</p>
                <input style={{ float: "left", marginTop: -25, gridRow:2, gridColumn:2}} type="range" min="1" max="50" defaultValue={props.support} id="support" onChange={(e)=> props.handleSupport(e.target.value)}/>
                <p style={{ float: "right" , paddingLeft: 10, gridRow:2, gridColumn:3}}>{props.support}</p>
        </div>
    )
}