import React, { useState } from "react";
import { Chart } from "./chart";
import { Options } from "./options"
import { Container, Row, Col } from 'react-bootstrap'

// <Chart width={600} height={600} request_params={{tag_val:"jazz", tag_name:"genres"}}/>

export default () => {

  const [requestParams, setRequestParams] = useState(null)

  const handleFilter = (e) => {
    setRequestParams({"tag_name":"genres","tag_val":e})
  }


  return (<>
    <Container fluid>
      <Row>
        <Col>
          <Options handleFilter={handleFilter}/>
        </Col>
      </Row>
      <Row>
        <Col>
          <Chart id={1} width={800} height={800} request_params={requestParams} />
        </Col>
      </Row>
    </Container>
  </>)
};
