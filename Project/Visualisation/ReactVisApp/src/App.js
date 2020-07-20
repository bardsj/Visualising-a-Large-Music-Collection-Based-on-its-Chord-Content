import React from "react";
import {Chart} from "./chart";

export default () => (
  <>
    <Chart width={600} height={600} request_params={{tag_val:"jazz", tag_name:"genres"}}/>
    <Chart width={600} height={600} request_params={{tag_val:"electronic", tag_name:"genres"}}/>
  </>
);
