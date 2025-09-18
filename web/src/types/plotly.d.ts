declare module 'plotly.js-dist-min' {
  import * as Plotly from 'plotly.js';
  export = Plotly;
}

declare module 'react-plotly.js/factory' {
  import type { PlotParams } from 'react-plotly.js';
  import type React from 'react';

  function createPlotlyComponent(Plotly: any): React.ComponentType<PlotParams>;
  export default createPlotlyComponent;
}