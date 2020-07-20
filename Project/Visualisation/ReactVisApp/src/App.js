import React, { useState } from "react";
import { ChartCircular, ChartParallel } from "./chart";
import { Options } from "./options"
import {VisParams} from "./visparams"
import { Container, Row, Col } from 'react-bootstrap'

// <Chart width={600} height={600} request_params={{tag_val:"jazz", tag_name:"genres"}}/>

export default () => {

  const [requestParams, setRequestParams] = useState({tag_val:"jazz", tag_name:"genres"})
  const [chartType, setChartType] = useState("Circular")

  const handleFilter = (e) => {
    setRequestParams({"tag_name":"genres","tag_val":e})
  }

  const handleChartType = (e) => {
    setChartType(e)
  }

  let chart = ""

  if (chartType == "Circular") {
    chart =  <ChartCircular id={1} width={800} height={800} request_params={requestParams} />
  }
  else  {
      chart = <ChartParallel id={1} width={800} height={800} request_params={requestParams} />
  }

  return (<>
    <Container fluid>
      <Row>
        <Col>
          <Options handleFilter={handleFilter} handleChartType={handleChartType}/>
        </Col>
      </Row>
      <Row>
        <Col>
          {chart}
        </Col>
      </Row>
      <Row>
        <Col>
          <VisParams />
        </Col>
      </Row>
    </Container>
  </>)
};
