import React, { useState, useEffect } from "react";
import { Form } from 'react-bootstrap';

export function VisParams(props) {

    const majminSel = (
        <div style={{ paddingLeft: 20, paddingBottom: 5, paddingTop: 10 }}>
            <input type="checkbox" id="cPaths" defaultChecked={props.requestParams.majMinSel} onChange={(e) => props.setRequestParams({ ...props.requestParams, majMinSel: e.target.checked })} />
            <label style={{ paddingLeft: 10, fontSize: 12 }} >Major/Minor Aggregation</label>
        </div>
    )

    let controls = ""

    if (props.requestParams.chartType.includes("Hierarchical")) {
        controls = (
            <div style={{ display: "grid", paddingLeft: 20, gridTemplateColumns: "50px 120px 50px" }}>
                <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 1, gridColumn: 1, fontSize: 12 }}>Focus</p>
                <input style={{ float: "left", marginTop: -25, gridRow: 1, gridColumn: 2 }} type="range" min="0.1" max="5" step="0.1" defaultValue={props.requestParams.focus} id="focus" onChange={(e) => props.setRequestParams({ ...props.requestParams, focus: e.target.value })} />
                <p style={{ float: "right", paddingLeft: 10, gridRow: 1, gridColumn: 3, fontSize: 12 }}>{props.requestParams.focus}</p>
                <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 2, gridColumn: 1, fontSize: 12 }}>{props.requestParams.fi_type == "hui" ? "Utility" : "Support"}</p>
                <input style={{ float: "left", marginTop: -25, gridRow: 2, gridColumn: 2 }} type="range" min="1" max="20" defaultValue={props.requestParams.support} id="support" onChange={(e) => props.setRequestParams({ ...props.requestParams, support: e.target.value })} />
                <p style={{ float: "right", paddingLeft: 10, gridRow: 2, gridColumn: 3, fontSize: 12 }}>{props.requestParams.support}</p>
            </div>
        )
    }
    else if (props.requestParams.chartType.includes("Parallel")) {
        controls = (
            <div>
                <div style={{ paddingLeft: 20, paddingBottom: 5, paddingTop: 10 }}>
                    <input type="checkbox" id="cPaths" defaultChecked={props.requestParams.cPaths} onChange={(e) => props.setRequestParams({ ...props.requestParams, cPath: e.target.checked })} />
                    <label style={{ paddingLeft: 10, fontSize: 12 }} >Colour paths by node start</label>
                </div>
                <div style={{ display: "grid", paddingLeft: 20, gridTemplateColumns: "50px 120px 50px" }}>
                    <div style={{ paddingLeft: 20, paddingBottom: 5, width: "200px" }}>
                        <Form.Group onChange={e => props.handleOptType(e.target.value)}>
                            <Form.Control size="sm" as="select">
                                <option>Root Node Order</option>
                                <option>Order by Support</option>
                            </Form.Control>
                        </Form.Group>
                    </div>
                    <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 1, gridColumn: 1, fontSize: 12 }}>Focus</p>
                    <input style={{ float: "left", marginTop: -25, gridRow: 1, gridColumn: 2 }} type="range" min="0.1" max="5" step="0.1" defaultValue={props.requestParams.focus} id="focus" onChange={(e) => props.setRequestParams({ ...props.requestParams, focus: e.target.value })} />
                    <p style={{ float: "right", paddingLeft: 10, gridRow: 1, gridColumn: 3, fontSize: 12 }}>{props.requestParams.focus}</p>
                    <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 2, gridColumn: 1, fontSize: 12 }}>{props.requestParams.fi_type == "hui" ? "Utility" : "Support"}</p>
                    <input style={{ float: "left", marginTop: -25, gridRow: 2, gridColumn: 2 }} type="range" min="1" max="20" defaultValue={props.requestParams.support} id="support" onChange={(e) => props.setRequestParams({ ...props.requestParams, support: e.target.value })} />
                    <p style={{ float: "right", paddingLeft: 10, gridRow: 2, gridColumn: 3, fontSize: 12 }}>{props.requestParams.support}</p>
                </div>
            </div>
        )
    }
    else {
        controls = (
            <div>
                <div style={{ paddingLeft: 20, paddingBottom: 5, width: "200px" }}>
                    <Form.Group onChange={e => props.handleOptType(e.target.value)}>
                        <Form.Control size="sm" as="select">
                            <option>Root Node Order</option>
                            <option>AVSDF</option>
                            <option>Baur Brandes</option>
                        </Form.Control>
                    </Form.Group>
                </div>
                <div style={{ display: "grid", paddingLeft: 20, gridTemplateColumns: "50px 120px 50px" }}>
                    <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 1, gridColumn: 1, fontSize: 12 }}>Focus</p>
                    <input style={{ float: "left", marginTop: -25, gridRow: 1, gridColumn: 2 }} type="range" min="0.1" max="5" step="0.1" defaultValue={props.requestParams.focus} id="focus" onChange={(e) => props.setRequestParams({ ...props.requestParams, focus: e.target.value })} />
                    <p style={{ float: "right", paddingLeft: 10, gridRow: 1, gridColumn: 3, fontSize: 12 }}>{props.requestParams.focus}</p>
                    <p style={{ float: "left", paddingRight: 10, paddingBottom: 5, gridRow: 2, gridColumn: 1, fontSize: 12 }}>{props.requestParams.fi_type == "hui" ? "Utility" : "Support"}</p>
                    <input style={{ float: "left", marginTop: -25, gridRow: 2, gridColumn: 2 }} type="range" min="1" max="20" defaultValue={props.requestParams.support} id="support" onChange={(e) => props.setRequestParams({ ...props.requestParams, support: e.target.value })} />
                    <p style={{ float: "right", paddingLeft: 10, gridRow: 2, gridColumn: 3, fontSize: 12 }}>{props.requestParams.support}</p>
                </div>
            </div>
        )
    }

    return (
        <div>
            {props.requestParams.chartType.includes("Sequence") ? null :majminSel}
            {controls}
        </div>
    )
}