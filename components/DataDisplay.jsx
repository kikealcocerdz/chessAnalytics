import React from "react";

function DataDisplay({ info }) {
  return (
    <div>
      {info ? <h1>{info.MRData.RaceTable.Races[0].raceName}</h1> : <div />}
    </div>
  );
}

export default DataDisplay;
