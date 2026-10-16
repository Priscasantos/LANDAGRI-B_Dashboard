/**
 * ECharts tree-shaking entry (Fase 2 fatia 2a/2b — reversible).
 *
 * Imports only what migrated routes use: BarChart + CustomChart (Gantt
 * fenológico) + HeatmapChart + LineChart + PieChart + ScatterChart +
 * RadarChart, Grid + Tooltip + Legend + MarkLine/MarkArea (mês atual, banda
 * de safra) + VisualMap + Radar + Polar + Timeline components, SVGRenderer. Nothing else from
 * `echarts` enters the `echarts` chunk — never `echarts/all`.
 */
import * as echarts from 'echarts/core';
import {
  BarChart,
  CustomChart,
  HeatmapChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
} from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkAreaComponent,
  VisualMapComponent,
  RadarComponent,
  PolarComponent,
  TimelineComponent,
} from 'echarts/components';
import { SVGRenderer } from 'echarts/renderers';
import { registerLandAgriThemes } from '../../../lib/echarts-theme';

echarts.use([
  BarChart,
  CustomChart,
  HeatmapChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkAreaComponent,
  VisualMapComponent,
  RadarComponent,
  PolarComponent,
  TimelineComponent,
  SVGRenderer,
]);

registerLandAgriThemes(echarts);

export { echarts };
export default echarts;
