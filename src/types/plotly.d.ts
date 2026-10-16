declare module 'plotly.js' {
  export interface DataTitle {
    text: string;
    font?: Partial<{ family: string; size: number; color: string }>;
    side?: string;
    x?: number;
    xanchor?: string;
  }

  export interface ErrorBar {
    type: string;
    symmetric: boolean;
    array: number[];
    value: number;
  }

  export type PlotType =
    | 'bar' | 'scatter' | 'histogram' | 'pie' | 'heatmap'
    | 'scatterpolar' | 'scattergl' | 'area';

  export type Datum = string | number | Date | null;
  export type TypedArray = Float32Array | Float64Array;

  export interface PlotData {
    type?: PlotType | string;
    x?: Datum[] | Datum[][];
    y?: Datum[] | Datum[][];
    z?: Datum[] | Datum[][] | Datum[][][];
    name?: string;
    mode?: string;
    text?: string[] | string[][];
    marker?: Partial<{
      color: string | string[];
      colors: string[];
      size: number | number[];
      opacity: number;
      line: Partial<{ color: string; width: number }> | Partial<{ color: string; width: number }>[];
      symbol: string | string[];
      colorscale: ColorScale;
      cmin: number;
      cmax: number;
      reversescale: boolean;
      showscale: boolean;
      colorbar: Partial<{ title: string | Partial<DataTitle>; x: number; thickness: number; len: number }>;
    }>;
    line?: Partial<{
      color: string;
      width: number;
      dash: string;
      shape: string;
      smoothing: number;
    }>;
    textposition?: string | string[];
    fill?: string;
    fillcolor?: string;
    stackgroup?: string;
    orientation?: 'v' | 'h';
    hovertemplate?: string;
    hoverinfo?: string;
    hoverlabel?: Partial<{ bgcolor: string; bordercolor: string; font: Partial<{ color: string; size: number; family: string }> }>;
    opacity?: number;
    nbinsx?: number;
    base?: number | string | (number | string)[];
    offset?: number;
    width?: number;
    showlegend?: boolean;
    legendgroup?: string;
    yaxis?: string;
    xaxis?: string;
    r?: number[];
    theta?: string[];
    textinfo?: string;
    texttemplate?: string;
    insidetextorientation?: string;
    hole?: number;
    labels?: (string | number)[];
    values?: number[];
    domain?: Partial<{ x: number[]; y: number[] }>;
    automargin?: boolean;
    title?: string | Partial<DataTitle>;
    colorscale?: ColorScale;
    zsmooth?: string | false;
    zmin?: number;
    zmax?: number;
    zhoverformat?: string;
    connectgaps?: boolean;
    customdata?: Datum[] | Datum[][];
    showscale?: boolean;
    colorbar?: Partial<{
      title: string | Partial<DataTitle>;
      thickness: number;
      len: number;
      x: number;
      y: number;
      outlinecolor: string;
      outlinewidth: number;
      tickfont: Partial<Font>;
      ticklen: number;
      tickwidth: number;
      ticks: string;
      thicknessmode: string;
      lenmode: string;
    }>;
    textfont?: Partial<Font>;
    insidetextanchor?: string;
    connector?: Partial<{ fillcolor: string; line: Partial<{ color: string; width: number; dash: string }> }>;
    decreasing?: Partial<{ marker: Partial<{ color: string }> }>;
    increasing?: Partial<{ marker: Partial<{ color: string }> }>;
  }

  export type Data = Partial<PlotData>;

  export type ColorScale = string | string[] | Array<[number, string]> | (string | number)[][];

  export interface Axis {
    title?: string | Partial<DataTitle>;
    type?: string;
    autorange?: boolean | 'reversed';
    range?: number[];
    tickangle?: number;
    tickfont?: Partial<{ family: string; size: number; color: string }>;
    tickformat?: string;
    tickmode?: string;
    tickvals?: number[] | string[];
    ticktext?: string[];
    nticks?: number;
    dtick?: number | string;
    showgrid?: boolean;
    gridcolor?: string;
    gridwidth?: number;
    zeroline?: boolean;
    zerolinecolor?: string;
    zerolinewidth?: number;
    showline?: boolean;
    linecolor?: string;
    linewidth?: number;
    showticklabels?: boolean;
    side?: string;
    overlaying?: string;
    anchor?: string;
    domain?: number[];
    position?: number;
    automargin?: boolean;
    categoryorder?: string;
    categoryarray?: (number | string)[];
    showspikes?: boolean;
    spikecolor?: string;
    spikethickness?: number;
    spikedash?: string;
    fixedrange?: boolean;
    layer?: string;
    visible?: boolean;
    color?: string;
    matches?: string;
    scaleanchor?: string;
    scaleratio?: number;
    constraintoward?: string;
  }

  export interface Legend {
    x?: number;
    y?: number;
    xanchor?: string;
    yanchor?: string;
    orientation?: 'v' | 'h';
    bgcolor?: string;
    bordercolor?: string;
    borderwidth?: number;
    font?: Partial<{ family: string; size: number; color: string }>;
    traceorder?: string;
    tracegroupgap?: number;
    itemsizing?: string;
    itemclick?: string;
    itemdoubleclick?: string;
    title?: Partial<{ text: string; font: Partial<{ family: string; size: number; color: string }> }>;
  }

  export interface Annotations {
    text: string;
    x?: number | string;
    y?: number | string;
    xref?: string;
    yref?: string;
    showarrow?: boolean;
    arrowhead?: number;
    ax?: number;
    ay?: number;
    font?: Partial<{ family: string; size: number; color: string }>;
    align?: string;
    bgcolor?: string;
    bordercolor?: string;
    borderwidth?: number;
    borderpad?: number;
  }

  export interface Shape {
    type?: string;
    x0?: number | string;
    x1?: number | string;
    y0?: number | string;
    y1?: number | string;
    xref?: string;
    yref?: string;
    fillcolor?: string;
    line?: Partial<{ color: string; width: number; dash: string }>;
    layer?: string;
  }

  export interface Font {
    family: string;
    size: number;
    color: string;
  }

  export interface Layout {
    title?: string | Partial<DataTitle>;
    font?: Partial<Font>;
    width?: number;
    height?: number;
    margin?: Partial<{ l: number; r: number; t: number; b: number; pad: number; autoexpand: boolean }>;
    paper_bgcolor?: string;
    plot_bgcolor?: string;
    showlegend?: boolean;
    legend?: Partial<Legend>;
    hoverdistance?: number;
    spikedistance?: number;
    hoverlabel?: Partial<{ bgcolor: string; bordercolor: string; font: Partial<Font>; namelength: number }>;
    dragmode?: string;
    hovermode?: string;
    barmode?: string;
    bargap?: number;
    bargroupgap?: number;
    barnorm?: string;
    boxmode?: string;
    colorway?: string[];
    annotations?: Partial<Annotations>[];
    shapes?: Partial<Shape>[];
    xaxis?: Partial<Axis>;
    yaxis?: Partial<Axis>;
    xaxis2?: Partial<Axis>;
    yaxis2?: Partial<Axis>;
    xaxis3?: Partial<Axis>;
    yaxis3?: Partial<Axis>;
    grid?: Partial<{ rows: number; columns: number; pattern: string; xgap: number; ygap: number }>;
    polar?: Partial<{
      radialaxis: Partial<Axis>;
      angularaxis: Partial<Axis>;
      sector: number[];
      bgcolor: string;
      hole: number;
    }>;
    ternary?: Partial<{
      sum: number;
      aaxis: Partial<Axis>;
      baxis: Partial<Axis>;
      caxis: Partial<Axis>;
    }>;
    scene?: Partial<{
      xaxis: Partial<Axis>;
      yaxis: Partial<Axis>;
      zaxis: Partial<Axis>;
      camera: Partial<{ eye: { x: number; y: number; z: number } }>;
    }>;
    geo?: Partial<{
      projection: Partial<{ type: string }>;
      scope: string;
      showland: boolean;
      landcolor: string;
      coastlinecolor: string;
      coastlinewidth: number;
      showcountries: boolean;
      countrycolor: string;
      countrywidth: number;
      lataxis: Partial<Axis>;
      lonaxis: Partial<Axis>;
    }>;
    updatemenus?: Partial<{ buttons: Partial<{ method: string; args: any[]; label: string }>[]; direction: string; showactive: boolean; type: string; x: number; xanchor: string; y: number; yanchor: string }>[];
    slider?: Partial<{ active: number; steps: { method: string; args: any[]; label: string }[]; x: number; pad: Partial<{ t: number; b: number }>; visible: boolean }>[];
    images?: Partial<{ source: string; x: number; y: number; sizex: number; sizey: number; xref: string; yref: string; layer: string }>[];
    separators?: string;
    hiddenlabels?: string[];
  }

  export interface Config {
    responsive?: boolean;
    displayModeBar?: boolean | 'hover';
    displaylogo?: boolean;
    showTips?: boolean;
    showLink?: boolean;
    plotlyServerURL?: string;
    linkText?: string;
    sendData?: boolean;
    showSources?: boolean;
    staticPlot?: boolean;
    editable?: boolean;
    edits?: Partial<{
      annotationPosition: boolean;
      annotationTail: boolean;
      annotationText: boolean;
      axisTitleText: boolean;
      colorbarPosition: boolean;
      colorbarTitleText: boolean;
      legendPosition: boolean;
      legendText: boolean;
      shapePosition: boolean;
      titleText: boolean;
    }>;
    toImageButtonOptions?: Partial<{
      format: 'png' | 'svg' | 'jpeg' | 'webp';
      width: number;
      height: number;
      scale: number;
    }>;
    modeBarButtonsToRemove?: string[];
    modeBarButtonsToAdd?: string[];
    modeBarButtons?: any;
    scrollZoom?: boolean;
    doubleClick?: string | false;
    doubleClickDelay?: number;
    globalTransforms?: any[];
    locale?: string;
    setBackground?: () => string;
  }

  export interface Template {
    layout?: Partial<Layout>;
    data?: Record<string, Partial<PlotData>>;
  }

  export function reactComponent(plot: any): any;
}

declare module 'react-plotly.js' {
  import type { Data, Layout, Config } from 'plotly.js';

  interface PlotParams {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    frames?: any[];
    revision?: number;
    style?: React.CSSProperties;
    className?: string;
    useResizeHandler?: boolean;
    onInitialized?: (figure: any) => void;
    onUpdate?: (figure: any) => void;
    onPurge?: (figure: any) => void;
    onError?: (err: Error) => void;
    onClick?: (event: any) => void;
    onHover?: (event: any) => void;
    onUnhover?: (event: any) => void;
    onSelected?: (event: any) => void;
    onDeselect?: (event: any) => void;
    onDoubleClick?: (event: any) => void;
    onRelayout?: (event: any) => void;
    onRestyle?: (event: any) => void;
    onRedraw?: () => void;
    onClickAnnotation?: (event: any) => void;
    onAfterPlot?: () => void;
    onBeforeHover?: (event: any) => boolean;
    onBeforeExport?: () => void;
  }

  const PlotComponent: React.FC<PlotParams>;
  export default PlotComponent;
}

declare module 'plotly.js-dist-min' {
  import type { Data, Layout, Config } from 'plotly.js';
  const Plotly: {
    react(container: HTMLElement, data: Data[], layout: Partial<Layout>, config: Partial<Config>): void;
    purge(container: HTMLElement): void;
  };
  export default Plotly;
}
