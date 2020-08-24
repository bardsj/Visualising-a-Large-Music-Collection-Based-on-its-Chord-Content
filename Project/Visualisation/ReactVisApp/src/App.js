import React, { useState } from "react";
import { ChartCircular } from "./chartCircular";
import { ChartParallel } from "./chartParallel";
import { ChartHier } from "./chartHier";
import { Options } from "./options"
import {VisParams} from "./visparams"
import {Legend} from "./legend"
import { Container, Row, Col } from 'react-bootstrap'
import { ChartHierSingleHue } from "./chartHierSingleHue";
import { ChartClust } from "./chartClust";
import { ChartParallelClust } from "./chartParallelClust";
import { ChartParallelSeq } from "./chartParallelSeq";
import { QueryTable } from "./queryTable";

// <Chart width={600} height={600} request_params={{tag_val:"jazz", tag_name:"genres"}}/>

export default () => {

  const [requestParams, setRequestParams] = useState({tag_val:["jazz"], tag_name:"genres",chartType:"Circular",focus:1,support:1,beta:1,optType:null,cPath:false,majMinSel:false})
  const [queryParams, setQueryParams] = useState({"chordSel":[]})

  const handleFilter = (e) => {
    if (e.target.checked == true) {
      requestParams.tag_val.push(e.target.value)
      setRequestParams({...requestParams,"tag_name":"genres","tag_val":requestParams.tag_val})
    }
    else {
      requestParams.tag_val = requestParams.tag_val.filter(x=> x!=e.target.value)
      setRequestParams({...requestParams,"tag_name":"genres","tag_val":requestParams.tag_val})
    }
  }

  const handleChartType = (e) => {
    setRequestParams({...requestParams,chartType:e})
  }

  const handleOptType = (e) => {
    if (e == "AVSDF") {
      setRequestParams({...requestParams,optType:"avsdf"})
    }
    if (e == "Baur Brandes") {
      setRequestParams({...requestParams,optType:"bb"})
    }
    if (e == "Root Node Order") {
      setRequestParams({...requestParams,optType:null})
    }
  }
 
  let chart = ""

  if (requestParams.chartType === "Circular") {
    chart =  <ChartCircular id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Parallel")  {
      chart = <ChartParallel id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Circular Hierarchical") {
    chart = <ChartHier id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Circular Hierarchical - Single Hue") {
    chart = <ChartHierSingleHue id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Circular Clustered") {
    chart = <ChartClust id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Parallel Clustered") {
    chart = <ChartParallelClust id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }
  else if (requestParams.chartType === "Parallel Sequence") {
    chart = <ChartParallelSeq id={1} width={800} height={800} request_params={requestParams} queryParams={queryParams} setQueryParams={setQueryParams}/>
  }

  let legend = ""
  if (requestParams.tag_val.length > 0 || requestParams.chartType == "Circular Hierarchical - Single Hue") {
    legend = <Legend requestParams={requestParams}/>
  }


  return (<>
    <Container fluid>
      <Row>
        <Col>
          <Options requestParams={requestParams} setRequestParams={setRequestParams} handleFilter={handleFilter} handleChartType={handleChartType}/>
        </Col>
      </Row>
      <Row>
      <Col sm={2}>
          <VisParams requestParams={requestParams} setRequestParams={setRequestParams} handleOptType={handleOptType}/>
        </Col>
        <Col>
          {chart}
        </Col>
        <Col sm={2}>
          {legend}
        </Col>
      </Row>
      <Row>
        <QueryTable queryParams={queryParams} requestParams={JSON.parse(JSON.stringify(requestParams))}/>
      </Row>
    </Container>
  </>)
};
